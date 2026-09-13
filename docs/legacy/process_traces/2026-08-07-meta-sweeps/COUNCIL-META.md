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
session id: 019fdda8-7b5c-7b51-8a15-9f14c0f4aa41
--------
user
COUNCIL-LOG META-AUDIT (read-only; no writes; final message = report). docs/council_log.md records C-001..C-049 with per-layer catches. Produce the layer-yield analysis the operation-loop meta-review needs: (1) for each review layer (pre-decision consult, implementation-audit lenses, delta re-audit, cold gate, refuter pairs, lead bench, CI, integration review, oversight/prune lens), count UNIQUE catches attributed across all entries and classify by severity where stated; (2) spend signals where recorded; (3) layers with zero unique catches over the last two+ sessions (drop candidates per the standing rule); (4) recurring LEAD error classes (piped-exit-status, stale RUN_STATE claims, index-row misses, etc.) with counts — the habits that have not stuck; (5) three concrete meta-process recommendations ranked by expected catch-per-token. Exact entry citations.
codex
I’ll audit the log as a dataset, deduplicate catches by underlying defect rather than mentions, and preserve exact C-entry citations. I’ll also check the repository’s current stop/queue state and review taxonomy before counting, since those define which sessions and layer names are authoritative.
exec
/bin/zsh -lc "pwd && rg --files -g 'AGENTS.md' -g 'RUN_STATE.md' -g 'TASK_QUEUE.md' -g 'AGENT_PLAN.md' -g 'docs/agent_playbook.md' -g 'docs/orchestration.md' -g 'docs/council_log.md' -g 'docs/contracts/*' | sort" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
AGENTS.md
AGENT_PLAN.md
RUN_STATE.md
TASK_QUEUE.md
docs/agent_playbook.md
docs/contracts/adapter_contracts.md
docs/contracts/analysis_plans.md
docs/contracts/bridge_protocol.md
docs/contracts/calibration_ledger.md
docs/contracts/capstone_scope.md
docs/contracts/claims_ladder.md
docs/contracts/doctor_preflight.md
docs/contracts/load_transition_alignment.md
docs/contracts/measurement_methodology.md
docs/contracts/node_worker_protocol.md
docs/contracts/powermetrics_fiducial.md
docs/contracts/publication_privacy.md
docs/contracts/quiet_guard.md
docs/contracts/run_bundle_layout.md
docs/contracts/token_normalization.md
docs/council_log.md
docs/orchestration.md
site_capsule/AGENTS.md

exec
/bin/zsh -lc "rg -n '"'^#{1,4} '"' RUN_STATE.md TASK_QUEUE.md docs/agent_playbook.md docs/orchestration.md AGENT_PLAN.md docs/council_log.md" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
docs/orchestration.md:1:# The Orchestration Process
docs/orchestration.md:12:## Roles: a lead, independent implementers/reviewers, and a human at the top
docs/orchestration.md:45:## The loop, end to end
docs/orchestration.md:110:### Stop cards and paused work
docs/orchestration.md:142:## The artifact system (where rigor becomes auditable)
docs/orchestration.md:189:## Council discipline
docs/orchestration.md:210:## Spend guardrails (WO-022; R2 ruled, Ed-ratified 2026-07-13)
docs/orchestration.md:261:## Topology: how it evolved (an example of the loop improving itself)
docs/orchestration.md:288:## What one session looks like (2026-07-07/08, the merge session)
docs/orchestration.md:306:## Reconstructing the loop on a clean machine
docs/orchestration.md:338:## Where to read the evidence
docs/council_log.md:1:# Council Log
docs/council_log.md:41:## Index
docs/council_log.md:86:## C-001: Review/counterreview adopted (Slice 2H)
docs/council_log.md:107:## C-002: Reverse review of the vertical-slice series; push vs PR
docs/council_log.md:155:## C-003: Research agenda expansion (ideation council)
docs/council_log.md:175:## C-004: Scored difficulty suites + per-run collection expansion
docs/council_log.md:207:# C-005: Steelmanned research agenda + workload expansion (ideation/strategy council)
docs/council_log.md:233:## Unique contributions per lens
docs/council_log.md:263:## Adjudications (steelman position → attack → reasoning → outcome)
docs/council_log.md:430:## What the devil's advocate killed outright (summary list)
docs/council_log.md:442:## Dissents
docs/council_log.md:451:## Process notes
docs/council_log.md:466:## C-006 (session trace + meta-review, 2026-07-07): six-stream parallel batch, integration review, process meta-review
docs/council_log.md:474:### Shape (orchestration decisions)
docs/council_log.md:507:### Catches (differential attribution)
docs/council_log.md:522:### Deliberations (design-bearing disagreements only)
docs/council_log.md:555:### Interventions (lead acted from outside the agents' self-reports)
docs/council_log.md:564:### Layer yield + spend (rough; spend capture starts next session)
docs/council_log.md:581:### Doctrine changes (adopted this session, each folded same-session)
docs/council_log.md:599:### Meta-review C-006 verdicts adopted (same session)
docs/council_log.md:620:### C-006 addendum (post-entry landings, same session)
docs/council_log.md:666:## C-007: Whole-project design/planning council + P2-013 fix design (user-directed)
docs/council_log.md:678:### Resolutions (what the consensus settled)
docs/council_log.md:766:### Deliberation trace (design-bearing disagreements)
docs/council_log.md:796:### Per-layer catches (instrumentation)
docs/council_log.md:813:### Follow-ups
docs/council_log.md:826:## C-008: Multi-stream session, checkpointed (2026-07-07 PM)
docs/council_log.md:846:## C-009: Meta-review of the orchestration system (SIGNED consensus)
docs/council_log.md:892:## C-010: Resume + merge session — C-009 topology first full run (2026-07-07/08)
docs/council_log.md:924:## C-011: Counter-review of the independent project critique (2026-07-08)
docs/council_log.md:994:## C-014: Workload-suite science hardening council (2026-07-08)
docs/council_log.md:1046:## C-015: Benchmark expansion council — suite architecture v2 + interop (2026-07-08)
docs/council_log.md:1105:## C-017: Suite-build adjudication + implementation gates (2026-07-08)
docs/council_log.md:1147:## C-018: D-013 alignment-capture window fix (2026-07-08)
docs/council_log.md:1168:## C-019: Post-suite-build meta-reassessment (2026-07-08)
docs/council_log.md:1217:## C-020: Stop-and-analyze whole project — technical + research merit debate (2026-07-08)
docs/council_log.md:1304:## C-021: Advisor status-site live-depth refresh (2026-07-09)
docs/council_log.md:1330:## C-023: Scientific-rigor review — suite, benchmark, question bank (2026-07-09)
docs/council_log.md:1384:## C-024: Spec-fleshing wave 1 — no-hardware artifact build (2026-07-09)
docs/council_log.md:1416:## C-025: Wave 2 — ultracode workflow build (2026-07-09)
docs/council_log.md:1447:## C-026: P2-034 broad campaign packs (2026-07-09)
docs/council_log.md:1456:## C-027: Whole-project council review with gpt-5.6-sol (2026-07-09)
docs/council_log.md:1514:## Index row
docs/council_log.md:1530:## Full entry
docs/council_log.md:1532:## C-028: C-027 adjudication and integration arc — infrastructure wave, PRs #49/#54/#55, and the integration window (2026-07-10/11)
docs/council_log.md:1680:## C-043: D-078 P0 instrument-repair close-out session — round-8 landing, round-9 final confirmation, sign-off (2026-07-22)
docs/council_log.md:1724:## C-044: NEG-8 estimand debate — peer disagreement adopted, Ed ratification (2026-07-24)
docs/council_log.md:1742:## C-045: NEG-8 screen+budget audit gauntlet — a new refuter pairing under A/B, four audit rounds, PR #85 (2026-07-24/25)
docs/council_log.md:1891:## C-038: FLOOR-LABEL-01 gauntlet close + quiet-window collection — an instrument-mix re-proportioning, a lost quiet window, and two exit codes that lied (2026-07-25/26)
docs/council_log.md:1906:### Layer catches (unique)
docs/council_log.md:1993:### Lead errors (recorded plainly)
docs/council_log.md:2027:### Collection outcomes
docs/council_log.md:2056:### Rough spend (estimates, not billing truth)
docs/council_log.md:2068:### Verdict and calibration
docs/council_log.md:2097:### Dictated-fact verification notes
docs/council_log.md:2118:## C-039 addendum: the FIX-6..9 gauntlet, three cold gates, and the 7B floor window (2026-07-29/30)
docs/council_log.md:2129:### Layers run
docs/council_log.md:2139:### Unique catches, by layer
docs/council_log.md:2205:### Window operation
docs/council_log.md:2219:### Process observations
docs/council_log.md:2232:### Addendum close-out (2026-07-30, later the same day)
docs/council_log.md:2260:## C-039 addendum II: two escalation consults — the cooldown-join design consult and the contrast-window recovery (2026-07-30/31)
docs/council_log.md:2267:### (i) Cooldown-join design consult → D5-J (2026-07-30)
docs/council_log.md:2310:### (ii) Contrast-window recovery consult (2026-07-31, live in-window)
docs/council_log.md:2361:## C-039 addendum III: the clock-anchor knife-edge consult (2026-08-01, in-window)
docs/council_log.md:2416:## C-040: The commit-3 gauntlet — five fix rounds, two cold gates, and what each layer uniquely caught (2026-08-01/02)
docs/council_log.md:2520:## C-040 addendum: the b-ii cold gate (D-106), the merge-fallback landings, and the codex envelope bug (2026-08-02/03)
docs/council_log.md:2599:## C-041: The D100-BII nested-closure arc — two more cold gates, a third-failure STOP, and the CAL-BRACKET consult (2026-08-03, desk session in Ed's absence)
docs/council_log.md:2686:## C-042: Ed-requested pre-ruling debate — 2 Sol xhigh rounds over the D-108/D-109 packets, both packets materially changed (2026-08-03)
docs/council_log.md:2723:## C-046: Retrospective — CAL-REBRACKET-01 max-bracket consumption gauntlet (2026-07-26)
docs/council_log.md:2740:## C-047: The 16h runway — two gauntlets, the winB STOP gate, the concurrent-sweep interception (2026-08-03)
docs/council_log.md:2763:## C-048: Integration-collision resolution — consult-shaped amendment, delta re-audit catches a live guard bypass (2026-08-04)
docs/council_log.md:2798:## C-049: The 12h autonomous marathon — issuance through the gate, six PRs, and the fork the first consumption exposed (2026-08-05/06)
docs/council_log.md:2828:### Unique catches, by layer
docs/council_log.md:2862:### Dispositions and open state at close
AGENT_PLAN.md:1:# Agent Implementation Plan
AGENT_PLAN.md:8:## Ground Rules For Agents
AGENT_PLAN.md:33:## Single Source Of Truth Map
AGENT_PLAN.md:58:## Canonical Architecture
AGENT_PLAN.md:71:## Phase Index
AGENT_PLAN.md:73:### Phase 1: Approval, Feasibility, And Measurement Design
AGENT_PLAN.md:118:### Phase 2: Harness, Mac Vertical Slice, And Homogeneous Baselines
AGENT_PLAN.md:166:### Phase 3: Disaggregation, Offline KV Replay, And Interconnect Sweep
AGENT_PLAN.md:191:### Phase 4: Core Characterization And Analysis
AGENT_PLAN.md:211:### Phase 5: Presentation, Repository Polish, And Final Submission
AGENT_PLAN.md:231:## Current Verification Command
AGENT_PLAN.md:243:# Phase 1: config + schema verbs
AGENT_PLAN.md:248:# Phase 2: run the harness (mock, deterministic) and verify the bundle
AGENT_PLAN.md:255:## Run Report Protocol
AGENT_PLAN.md:274:## Task Queue Protocol
docs/agent_playbook.md:1:# Agent Playbook: Ordered Missions
docs/agent_playbook.md:24:## How To Pick A Mission
docs/agent_playbook.md:50:## Mission M0: Preflight (every session)
docs/agent_playbook.md:91:## Mission M1: Slice 2N — Pre-Hardware Hardening (queue P2-007)
docs/agent_playbook.md:121:### 2N.1 `RunContext` seam + raw evidence
docs/agent_playbook.md:143:### 2N.2 Measured window excludes sampler startup
docs/agent_playbook.md:162:### 2N.3 Reducer token-count fallback
docs/agent_playbook.md:178:### 2N.4 Rail-summation timestamp contract
docs/agent_playbook.md:193:### 2N.5 Config schema accepts emitted configs
docs/agent_playbook.md:212:### 2N.6 Post-hoc `reduce` verb + structured reducer failures
docs/agent_playbook.md:228:### 2N.7 Report/reducer rail-policy alignment (via 2N.8)
docs/agent_playbook.md:240:### 2N.8 Shared bundle read layer (`BundleReader`)
docs/agent_playbook.md:258:### 2N.9 Schema v0.2 compatibility check (design-only, no code required)
docs/agent_playbook.md:279:## Mission M2: Measurement-Corpus Backup Protocol (queue P0-002)
docs/agent_playbook.md:300:## Mission M3: Background / Related-Work Draft (queue P3-001, Stage 4.6)
docs/agent_playbook.md:323:## Mission M4: Close D-016 Model Selection (queue P2-004)
docs/agent_playbook.md:346:## Mission M5: Slice 2G — MLX Runtime Adapter (part of queue P2-003)
docs/agent_playbook.md:366:## Mission M6: Slice 2H — powermetrics Telemetry Adapter
docs/agent_playbook.md:386:## Mission M7: Slice 2I — Mac Vertical Slice (the flagship)
docs/agent_playbook.md:407:## Mission M8: Slices 2K/2L — Remote Targets
docs/agent_playbook.md:434:## Mission M9: Slice 2M — Homogeneous Baselines
docs/agent_playbook.md:451:## Mission M10: Phase 3 Stage 3.0 — KV Feasibility Spikes
docs/agent_playbook.md:470:## After Any Mission
RUN_STATE.md:1:# JouleWise Run State
RUN_STATE.md:16:## ⏳ 2026-08-07 — paper-first session (LIVE; block 2, refreshed post-burn)
RUN_STATE.md:51:## ✅ CHECKPOINT 2026-08-06 late — machine-move stop (resume script)
RUN_STATE.md:105:## ⏳ 2026-08-06 AFTERNOON — re-mint fork: historical consumption is closed at main; Ed's ruling owed
RUN_STATE.md:160:## ✅ CHECKPOINT 2026-08-06 morning — executed by the afternoon session above
RUN_STATE.md:246:## ⏳ 2026-08-05 LATE NIGHT — Fable resume: all 4 audits harvested, D-115 adjudicated, two Sol rounds in flight
RUN_STATE.md:303:### Overnight progress ledger (updated ~23:50; all evidence in .desk + session scratchpad, custody commits as noted)
RUN_STATE.md:346:### D-079 ISSUANCE HELD by cold gate (recorded ~03:30 2026-08-06) — issuance is IMPLEMENTATION, not an edit
RUN_STATE.md:373:### GOVERNING PRIORITY STACK (Ed, 2026-08-06) — all work serves the paper
RUN_STATE.md:382:### SYLLABUS ANCHOR (Ed, 2026-08-06) — the overarching goal
RUN_STATE.md:392:### QG census — magistrate stop-condition set (recorded ~02:40 2026-08-06)
RUN_STATE.md:411:### ESCALATION TRIGGER FIRED — quiet-guard observation-failure→absence class (recorded ~01:15 2026-08-06)
RUN_STATE.md:427:### Ed directive batch (2026-08-05 ~22:00, in-thread; 12-hour autonomous window)
RUN_STATE.md:449:## ✅ CHECKPOINT 2026-08-05 night — Ed model-switch stop (successor is FABLE; read this, then the EVENING queue)
RUN_STATE.md:457:### What landed this session (pushed; main green at `b55008f`)
RUN_STATE.md:476:### IN FLIGHT at checkpoint — harvest, do NOT re-run blind
RUN_STATE.md:508:### Next substantive item (un-gated payoff)
RUN_STATE.md:516:### Standing facts unchanged
RUN_STATE.md:522:## ✅ CHECKPOINT 2026-08-05 evening — DESCOPE + RESUME SCRIPT (still-valid queue; NIGHT block above updates it)
RUN_STATE.md:535:### SUCCESSOR'S QUEUE — start here, all agent-startable desk work
RUN_STATE.md:552:### What landed this session (all pushed; main green)
RUN_STATE.md:569:### IN FLIGHT at checkpoint (harvest from disk — do NOT re-run blind)
RUN_STATE.md:583:### DESCOPE — what is SHELVED (do not build; reopen only on Ed's word)
RUN_STATE.md:595:### Design record worth keeping (from the credential consult, before descope)
RUN_STATE.md:609:### Follow-on rows to register (queued this checkpoint)
RUN_STATE.md:625:### Standing operating facts (unchanged, still binding)
RUN_STATE.md:642:## ✅ 2026-08-05 — Ed's decision batch executed (PR #100 merged; acks recorded; quiet-guard ruled)
RUN_STATE.md:685:## ✅ CHECKPOINT 2026-08-04 ~06:30 — Ed-ordered stop (successor script)
RUN_STATE.md:730:## ✅ CHECKPOINT 2026-08-04 early AM — T3 HANDOFF (successor script)
RUN_STATE.md:743:### What landed overnight (all pushed; nothing dangling)
RUN_STATE.md:849:### ED OWES (nothing blocks the successor's queue)
RUN_STATE.md:869:### Standing operating facts for the successor
RUN_STATE.md:888:## ✅ CHECKPOINT 2026-08-03 late night — T3 CUTOVER (successor session, ACTIVE)
RUN_STATE.md:1025:## ✅ CHECKPOINT 2026-08-03 night — 16h-runway stream state (successor is FABLE, MAGISTRATE, on T3 Code)
RUN_STATE.md:1133:## DESK-SESSION UPDATE (HISTORICAL — superseded by the checkpoint block at top) (2026-08-03, Ed away — first the cold-gate arc, then a sleep-window of non-claim rows) — read this, then the two ⏸️ blocks above
RUN_STATE.md:1225:## EXECUTED RESUME SCRIPT (2026-08-02 ~16:10 PT checkpoint — FULLY EXECUTED by the 2026-08-03 desk session; see the DESK-SESSION UPDATE above; retained as historical record)
RUN_STATE.md:1354:## PRIOR RESUME SCRIPT (2026-08-01 desk session, second checkpoint; resume EXACTLY here)
RUN_STATE.md:1455:## PRIOR ACTIVE RESUME SCRIPT (2026-08-01 ~07:00 PT checkpoint; EXECUTED this desk session — retained for the collection facts)
RUN_STATE.md:1563:## PRIOR ACTIVE RESUME SCRIPT (2026-07-31 ~22:15 PT checkpoint; EXECUTED — window A verdict emitted [FAILED], window B run and salvage-closed; retained for the collection facts)
RUN_STATE.md:1667:## PRIOR STATE (2026-07-31 claims-desk close-out; resume script below FULLY EXECUTED)
RUN_STATE.md:1759:## EXECUTED RESUME SCRIPT (2026-07-30 19:15 PT pre-window checkpoint; historical — fully executed, see CURRENT STATE)
RUN_STATE.md:1838:## PRIOR STATE (2026-07-30 afternoon; the resume script below is EXECUTED except where struck)
RUN_STATE.md:1860:## EXECUTED RESUME SCRIPT (2026-07-30 ~11:00 PT handoff checkpoint; historical)
RUN_STATE.md:1988:## Start Here For Every Big Run
RUN_STATE.md:2037:## Historical Stop-Card Note
RUN_STATE.md:2043:## ACTIVE_STOP_CARD
RUN_STATE.md:2047:## Active Global Work-Selection Gates
RUN_STATE.md:2051:## Restart By Machine-State Lane
RUN_STATE.md:2055:### [ED-EXTERNAL]
RUN_STATE.md:2059:### [QUIET-MAC]
RUN_STATE.md:2063:### [AGENT]
RUN_STATE.md:2069:## CHECKPOINT 2026-07-18 (late): D-077 adversarial arc complete, PR #77 open
RUN_STATE.md:2093:## CHECKPOINT 2026-07-18: Claude script bridge runs in the pet's app task
RUN_STATE.md:2119:## CHECKPOINT 2026-07-17 (late session): env-guard branch open, review pending
RUN_STATE.md:2170:## Superseded stop card (CP-5)
RUN_STATE.md:2182:## Current Project Status
RUN_STATE.md:2189:### The central measurement fact (read before any measurement decision)
RUN_STATE.md:2201:### Collection state
RUN_STATE.md:2235:### The critical path: build the mint (HISTORICAL — CLOSED 2026-07-30)
RUN_STATE.md:2270:### Disk
RUN_STATE.md:2294:### Orchestration
RUN_STATE.md:2302:### What needs Ed
RUN_STATE.md:2381:## Session History (pointers only — run reports own the narrative)
RUN_STATE.md:2503:## Current Verification
RUN_STATE.md:2600:### Historical verification archive (exact at the recorded heads)
RUN_STATE.md:2743:## Known Workspace State
RUN_STATE.md:2810:## Historical Next-Work Snapshot (superseded 2026-07-15)
RUN_STATE.md:2828:## Reference Decisions And Blockers (non-selection context)
TASK_QUEUE.md:1:# JouleWise Task Queue
TASK_QUEUE.md:6:## Intake Rule For New Tasks
TASK_QUEUE.md:34:## Priority Scale
TASK_QUEUE.md:47:## Ranking Factors
TASK_QUEUE.md:65:## Ready/Shelf Rule
TASK_QUEUE.md:80:## Machine-State Lanes (adopted C-007, 2026-07-07)
TASK_QUEUE.md:92:## Historical Queue Snapshot (superseded 2026-07-15)
TASK_QUEUE.md:98:## Completed Queue Items
TASK_QUEUE.md:184:## Shelved Follow-Ups With Triggers (C-027 disposition ledger — REV-10)
TASK_QUEUE.md:213:## Current Do-Not-Do-Yet List
TASK_QUEUE.md:241:## Queue Maintenance
TASK_QUEUE.md:254:## Intake Batch Owed To The Kernel (2026-07-30/31)
TASK_QUEUE.md:306:## Current Queue
TASK_QUEUE.md:384:## Active Global Work-Selection Gates
TASK_QUEUE.md:388:### [ED-EXTERNAL] lane
TASK_QUEUE.md:399:### [QUIET-MAC] lane
TASK_QUEUE.md:412:### [AGENT] lane
TASK_QUEUE.md:462:### Shelved task records

exec
/bin/zsh -lc "sed -n '1,90p' RUN_STATE.md; sed -n '2037,2068p' RUN_STATE.md; sed -n '2182,2315p' RUN_STATE.md; sed -n '2743,2810p' RUN_STATE.md; sed -n '1,90p' TASK_QUEUE.md; sed -n '184,240p' TASK_QUEUE.md; sed -n '306,462p' TASK_QUEUE.md; sed -n '50,90p' docs/agent_playbook.md; sed -n '1,75p' AGENT_PLAN.md; sed -n '142,260p' docs/orchestration.md" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
# JouleWise Run State

This file is the single running pointer for the project: the one doc to
read to get back here. Session records live in `docs/run_reports/` and
`docs/process_traces/`; deliberation lives in `docs/council_log.md`;
policy lives in `docs/decision_log.md`. The three dated restart docs
`docs/process_traces/RESUME-2026-07-26.md`, `RESUME-2026-07-27.md`, and
`RESUME-2026-07-28.md` are now point-in-time session records only — each
carries a superseded banner, and everything still current in them is
folded in below. Do not create another dated restart doc; update this
file instead.

Last updated: 2026-08-07 — **LIVE SESSION (14h Ed window). Read this
block first;** the 2026-08-06 checkpoint below is executed history.

## ⏳ 2026-08-07 — paper-first session (LIVE; block 2, refreshed post-burn)

**Landed this session (all on main):** **D-117** transcribed + index row
(three prospective windows; supersession lines on D-110/D-113;
CLAIMS_STATUS un-staled). **MVP paper draft COMPLETE — PR #110 MERGED**
(`6a70707`): full structure, 18 refs, round-2 gauntlet (2 lenses +
bibliography audit + xhigh fix round + delta re-audit + bench fidelity
corrections incl. interval-average integration). **Plan-freeze design
memo ratified** (`docs/process_traces/2026-08-07-d117-plan-freeze/` —
U1-U10 work orders, gates 1-8, budgets 3.14/3.24/2.80 h). **Night-
hardening register** (3 Sol lenses + paper-vs-code fidelity audit;
R6 path-doubling live; L4/L5 ledger gaps; URGENT pre-window reason-code
plumbing). **Paper-portfolio factory** (Ed-ordered burn): 24 Sol-fast
proposals + 24 Opus counter-reviews + dual xhigh syntheses + magistrate
ADJUDICATION (`docs/strategy/2026-08-07-paper-portfolio/`) — arc:
MVP+WindowC → quantization BF16/Q4/Q8 → MoE stretch; 7 riders into MVP;
Ed's ranked rulings ##1-7 in ADJUDICATION.md. **Three-night operator
packet** (pre-freeze edition, `docs/strategy/2026-08-07-three-night-
operator-packet.md`). Earlier: t3appup analysis banked; prefill
feasibility custodied; C-049; skill-usage log.

**IN FLIGHT (harvest, do not re-run):** U1 DONE-with-NEEDS_SCOPE →
scope GRANTED → **U1b writer integration running** (worktree
`<scratchpad>/u1`, branch impl/d117-u1-ledger-session, 79 focused tests
green on the completed core). **U3 DONE** (pinset v2 + four-cell mint,
v1 parity; worktree `<scratchpad>/u3`, branch impl/d117-u3-pinset-v2)
— **two audit lenses running** (contract + execution). Next: U3 triage/
fix/delta → PR; U1b harvest → audit → U2 (cold-gated) → U4; then U5-U7
packs. **Ed's rulings owed:** ADJUDICATION.md ##1-7 (top: Window C
night; reported-energy cells before pack freeze; reason-code plumbing).

**Worktrees:** `<scratchpad>/desk` (main, bookkeeping), `<scratchpad>/u1`,
`<scratchpad>/u3`. Main tree: detached on merged paper branch — prune at
close. Owed at close: run report, council entry, sweep, skill-usage.

## ✅ CHECKPOINT 2026-08-06 late — machine-move stop (resume script)

**Nothing in flight; nothing unpushed after this commit.** All background
jobs harvested; consult custodied; campaign logs sha-verified untouched.

**STATE IN ONE BREATH:** PR #109 merged (`c537386`); first consumption
attempt proved the historical re-mint structurally closed at main (see
AFTERNOON block + `docs/process_traces/2026-08-06-d110-remint-fork/`);
Sol xhigh + magistrate recommend Option 2 (three fresh prospective
windows); **Ed has NOT yet ruled** — he was probing costs when the
session stopped.

**Ed's in-thread directives this exchange (record, not yet decision-log):**
1. **MVP claim scope: "a little more than just decode, at least
   decode/prefill."** Magistrate's proposed shape (not yet Ed-acked):
   prefill FLOOR cells ride both fresh floor windows cheaply; a prefill
   CONTRAST first gets a labelled non-claim desk feasibility check from
   historical diagnostics against the D-078 ~5 J effective bar — if it
   clears, the contrast window grows a prefill ABBA arm; if not, prefill
   floors are claimed, contrast stays decode-only, and the infeasibility
   becomes a limitations paragraph.
2. **Ed challenged the zero-agent window rule** ("why can't you be
   running quietly?"). Owed answer components, for the successor: (a)
   physics at our bar — a bursty resident agent stack at ~0.1–0.5 W over
   minute-scale members is joules-to-tens-of-joules gross vs a ~5 J
   effective bar; idle subtraction cancels only the steady part; every
   CLAIM window to date was zero-agent; the app-resident mode was only
   ever used for fenced NON-claim characterization. (b) The banked
   `runs_char_t3appup_20260804_r01/_r02` captures exist precisely to
   QUANTIFY the dormant-app delta — **desk analysis queued (protocol
   §Analysis: mean/p95 package power from rich_telemetry_idle.jsonl)**;
   run it and give Ed a NUMBER. (c) The honest reframe: the binding
   presence constraint is §5A's sudo (network-time toggle), not the
   zero-agent rule; the agent-armed window design (QUIET-GUARD two-phase
   handoff, commits 2–4 + a scoped sudoers rule for the two systemsetup
   commands) exists and was descoped by Ed's OWN ruling as not worth the
   security-critical code — reopenable on his word if three fresh
   windows change his calculus.
3. Ed confirmed understanding that Option 2 = recollect the science
   windows (~3 windows, bookend-presence only) while everything else
## Historical Stop-Card Note

This 2026-07-11 clearance note is retained as history only; current stop-card
and work-selection state is generated immediately below from the kernel.

<!-- BEGIN GENERATED: state-kernel run-state-intake -->
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
canonical **operative decode floor is 7.377086 J**, and that is the hard
six-decimal literal pinned in `scripts/mint_floor_artifact.py`. D-079
clause 5's "3.592138" pin predates window C's comparative extraction and
is superseded for the operative figure; both components remain published
and LABELLED per D-078 clause 11.

### The critical path: build the mint (HISTORICAL — CLOSED 2026-07-30)

All four blockers below are closed and this section is retained as
chronology only: `scripts/mint_floor_artifact.py` is the non-test call
site (1), the 30-vs-37 basis question RESOLVED (2), `production_window`
is in `_CALIBRATION_SCOPES` (3), and `impl/floor-mint` merged via PR #87
(4). Mint #1 merged via PR #88 at `da83337`.

`build_floor_cell` / `build_floor_artifact` / `build_absolute_record` /
`build_comparative_record` in `joulewise/detection_floor.py` have zero
non-test call sites; `scripts/extract_detection_floors.py` writes an
extraction report and stops. Established blockers:

1. **`claim_ready` requires an absolute AND a comparative record in the
   SAME cell**, so a10 alone mints a structurally `smoke_only` artifact.
   Mint #1 must pair a10's absolute cell with window C's decode
   comparative. Verifying that the two share backend, metric,
   `window_class`, condition family, and stack identity is a GO/NO-GO,
   not a task.
2. **A 30-vs-37 member authentication mismatch:** the a10 phase spec
   selects 30 members; the passed verdict authenticates 37. Extraction of
   the authenticated basis takes **20 min 36 s** on real data — budget
   for it.
3. **Windows C and D have no legal `calibration_scope`.**
   `_CALIBRATION_SCOPES` is `("window_a", "window_b_revalidation",
   "smoke")`. D-079 clause 4 adopts one general production name; proposed
   literal `production_window`.
4. **Pre-mint schema hardening was then written but unmerged** (it
   merged via PR #87; the branch is on main): branch
   `impl/floor-mint` @ `617060a` (pushed) makes the extraction report
   export the admissible half-widths it already computes, and moves
   `_WIDENED_FLOOR_KEYS` from optional into the required key sets so
   width ABSENCE is a schema error rather than a silent fall-back to the
   point-only floor. Suite 2198 OK.

### Disk

**EXECUTED 2026-07-28 (Ed-authorized 2026-07-27: iCloud-only acceptable,
delete after verified upload — resolving both open disk questions).**
Disk now has **115 GB free** (was 33 GB; ~61 GB freed by the repo prune described below, the rest by unrelated local housekeeping). The selective-prune plan was
generalized to every runs corpus: all 27 corpora are archived in
`~/Library/Mobile Documents/com~apple~CloudDocs/JouleWise-backup/` with a
per-corpus `MANIFEST.sha256`. Verification before any deletion: APFS-clone
name+byte parity; `brctl evict` of 100% of files (evict success = upload
complete); rematerialize-and-rehash of 20,028 files from iCloud (100% of
small evidence files + sampled traces) against the manifests — 0
mismatches. Then 1,848 `powermetrics*.plist` traces ≈ 61 GB were deleted
locally; **every small evidence file remains resident**, each pruned dir
carries `PRUNED.md` + `MANIFEST.sha256`. Restoring any trace =
`brctl download` its path under the archive.

Kept fully local (no deletion): `runs_window_a10_20260725(+_bound)` and
`runs_window_c_20260726(+_bound)` (mint #1 inputs),
`runs_window_a5_quarantine` (quarantine is evidence), and in `runs/` the
six frozen acceptance-gate bundles (`example-mac-mlx-*`) + `experiments/`
custody — the retained-corpus strict gate re-ran green post-prune (3/3,
incl. six-bundle strict validation), and keep-list file counts verified
unchanged.

### Orchestration

Global `CLAUDE.md` hard rule 11 now defines the topology: Fable as
MAGISTRATE and Ed's direct, Opus 5 as LIEUTENANT / operational chief, a
cold-Fable-instance gate with mandatory (not discretionary) triggers, and
an enumerated forbidden-to-decide-alone list for the lieutenant. D-080's
standing fresh-eyes sweep is the first exercise of that list.

### What needs Ed

1. RESOLVED 2026-07-27/28: Ed answered both disk questions (iCloud-only
   acceptable; delete after verified upload) and the archive+prune
   executed — see "Disk" above. Note the traces are now iCloud-only
   (single durable copy); flag if a second physical copy is wanted.
2. **AC power** for measurement windows — the production policy requires
   it and the machine was on battery.
3. A magistrate ruling on a conflict between D-080 and D-061: D-080's
   anti-ritual clause 4(ii) evaluates a rotating lens against the
   two-zero-sessions drop rule, which D-061 explicitly superseded with an
   expected-loss adjudication ("three applicable exposures TRIGGER an
   expected-loss review decision, never automatic deletion").
4. `FLOOR-WORKLOAD-SIZING-01` — resizing floors resizes the science, so
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
# JouleWise Task Queue

This is the live queue for JouleWise work. When the user gives a new task, first
triage it here instead of assuming it should happen immediately.

## Intake Rule For New Tasks

For every new user task:

1. Read `RUN_STATE.md`.
2. Read this file.
3. Check `git status --short --branch`.
4. Review the last 2-3 commits with `git log --oneline --decorate -3`.
5. Check relevant handoffs in `docs/run_reports/`.
6. If `RUN_STATE.md` contains an ACTIVE `ACTIVE_STOP_CARD`, that card
   outranks this queue. Execute or preserve the card's resume/cleanup
   instructions before considering any lower-ranked work.
7. Decide whether the task is:
   - urgent workspace hygiene,
   - Phase 1 evidence work,
   - Phase 2 implementation prep,
   - later-phase research work,
   - documentation/reporting,
   - or unrelated/new scope.
8. Place or update the task in the queue with priority, rationale, evidence,
   and blockers.
9. If executing it now, say why it outranks the current top task.
10. Closure rule (D-023): a row may move to Completed only after the
    corresponding phase exit-checklist matrix row already shows the same
    status with dated evidence, and the Completed row's evidence cell
    must cite that matrix row (file + item id). If no matrix row exists
    for the work, say so explicitly in the evidence cell.

## Priority Scale

- **P0 Safety**: prevents accidental data loss, bad commits, broken handoffs, or
  corrupted repo state.
- **P1 Phase Gate**: required to close the current phase or unblock the next
  phase responsibly.
- **P2 Next Slice**: next implementation slice after current phase gates are
  adequately planned or closed.
- **P3 Research Expansion**: useful experiment or feature, but not needed for
  current gate.
- **P4 Polish**: quality-of-life, dashboard polish, formatting, cleanup, or
  presentation work.

## Ranking Factors

Rank higher when a task:

- Prevents accidental loss or bad Git history.
- Produces evidence for the current phase exit checklist.
- Removes ambiguity for multiple later steps.
- Is required before physical hardware time is spent.
- Is cheap to verify and reduces future confusion.
- Matches the current phase better than jumping ahead.

Rank lower when a task:

- Depends on unavailable hardware or supervisor input.
- Is a later-phase feature.
- Adds polish before a runnable vertical slice exists.
- Produces code without a clear run-bundle or test artifact.

## Ready/Shelf Rule

A partially built or proposed task is **READY** only when it has:

- one authority document or stream-log pointer,
- bounded files/modules or a bounded artifact target,
- explicit acceptance evidence or a verification command,
- no hidden hardware/user/token-budget dependency, and
- a named lane (`[AGENT]`, `[QUIET-MAC]`, or `[ED-EXTERNAL]`).

If any of those are missing, keep the item as a shelved concept or
planning note instead of letting it compete with executable queue work.
Half-finished work should be resumed only through its authority pointer
and stop-card/checkpoint state, not by inference from prose summaries.

## Machine-State Lanes (adopted C-007, 2026-07-07)

Every task carries a lane; a session picks the top task COMPATIBLE with
its machine state, not the top task absolutely:

- **[QUIET-MAC]** — measurement campaigns only: no agent fleet, no Codex
  load, idle gate will flag contamination.
- **[AGENT]** — code, docs, feasibility spikes; safe during agent-heavy
  sessions.
- **[ED-EXTERNAL]** — needs the user: advisor, calendar, device access,
  purchases, destinations.
## Shelved Follow-Ups With Triggers (C-027 disposition ledger — REV-10)

- **SOL-FAST-TIER (verified 2026-08-03, Ed aside):** Codex FAST MODE
  works on live Sol calls: `-c service_tier=fast` accepted at the bench
  (documented: 1.5x speed, 2.5x ChatGPT-credit consumption on GPT-5.6;
  `/fast on` interactively; persist via config `service_tier="fast"` +
  `[features].fast_mode=true`). `-c service_tier=priority` (API
  priority tier) also accepted. `~/.codex/config.toml` stays pinned
  `default`; NOT built into any process per Ed. Trigger: latency-
  critical Sol runs (live debugging, Ed-waiting consults) may pass the
  flag per-call; any standing default change is Ed's call (2.5x quota
  burn interacts with the usage-pressure memory).

Previously promised follow-ups whose queue rows had silently died; each
now has an explicit disposition:

- D-013 SSH-controlled vs co-resident controller comparison — SHELF,
  trigger: first 2K live session (validation cell rides that session).
- Empirical corpus for the 0.40 GPU-idle contamination threshold — SHELF,
  trigger: Window-A calibration data exists (P2-015 output feeds it).
- `dvfm_states` slimming option — SHELF, trigger: bundle-size pain during
  the 2M campaign; otherwise declined as premature.
- Cold-load / model-load-energy capture — DECLINED for the capstone scope
  (CP-5 deferral made permanent unless an AP row claims it; warm-cache
  protocol is the declared scope).

- CI-003 developer polish (console script, macOS CI job, Ruff, coverage thresholds) — SHELF, trigger: G6-equivalent reference release (hardening adjudication C10).
- DOC-010 historical-archive audit — SHELF, trigger: DOC-008 state kernel proven in use (hardening adjudication C11).

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
|---|---|---|---|---|---|
| E1 | P1-008 | P1 Phase Gate | READY | Map phases to the academic calendar and capture the evaluator acceptance bar (minimum figures, demo expectation, reproducibility threshold, Mac-only plus split-deferral acceptability). | Colloquium/report dates plus borrow window in docs/milestones.md; phase targets derived; acceptance-bar notes beside the P1-001 scope notes. Evidence: Dates + borrow window in docs/milestones.md; Derived phase targets; Acceptance-bar notes beside P1-001 scope notes. Authority: [Milestones + R-012](docs/milestones.md). Acceptance: [P1-008 acceptance](docs/process/state_kernel.json). Note: R-012 is the biggest active management risk for an undergrad timeline. |
| E2 | P2-027 | P2 Next Slice | READY | Publish a privacy-transformed, integrity-verified three-bundle pack from a clean tagged commit and obtain one documented external re-reduction by an uninvolved party. | Published pack plus a documented external re-reduction; until then the auditability claim stays L0-scoped. Evidence: Published pack; Documented external re-reduction. Authority: [C-020 + C-027 NEG-9](docs/reviews/2026-07-09-c027-whole-project-review.md). Acceptance: [P2-027 acceptance](docs/process/state_kernel.json). Note: Environment locks, pack preparation, integrity tooling, and fail-closed privacy transformation are merged; publication and external re-reduction remain ED-EXTERNAL. |
| E3 | P1-001 | P1 Phase Gate | READY | Capture supervisor approval and scope notes. | Dated notes in the Phase 1 exit checklist; unblocks full D-016 closure (P2-004). Evidence: Dated notes in docs/phase_1/phase_1_exit_checklist.md. Authority: [R-001](docs/risk_register.md). Acceptance: [Phase 1 exit checklist](docs/phase_1/phase_1_exit_checklist.md). Note: User-deferred 2026-07-06; R-001 mitigation holds: all work stays harness-shaped. |
| E4 | P1-003 | P1 Phase Gate | READY | Record the wall-meter decision: meter make/model or unavailable verdict plus measurement/export method. | Exit-checklist wall-meter section filled; informs D-018 boundary calibration. Evidence: Wall-meter section of the Phase 1 exit checklist filled. Authority: [D-018/C-003](docs/decision_log.md). Acceptance: [Phase 1 exit checklist](docs/phase_1/phase_1_exit_checklist.md). Note: Elevated value: gates Q6 boundary sensitivity (C-003). |
| E5 | P1-004 | P1 Phase Gate | READY | Fill the network/interconnect topology plan: physical topology, link-speed paths, throughput method. | Network section of the Phase 1 exit checklist recorded. Evidence: Network section of the Phase 1 exit checklist recorded. Authority: [R-011](docs/risk_register.md). Acceptance: [Phase 1 exit checklist](docs/phase_1/phase_1_exit_checklist.md). Note: Partial. |
| E6 | P1-006 | P1 Phase Gate | READY | Confirm NVIDIA/Orin telemetry access paths: SSH/runtime/telemetry command evidence, or marked pending with blocker (gates slices 2K/2L). | Instrumentation section of the Phase 1 exit checklist filled or blocker recorded. Evidence: SSH/runtime/telemetry command evidence in the exit checklist; Or an explicit pending-with-blocker record. Authority: [Remote gate / NV-GATE-2](docs/phase_2/hardware_slice_implementation_guide.md). Acceptance: [Phase 1 exit checklist](docs/phase_1/phase_1_exit_checklist.md). |

### [QUIET-MAC] lane

| Rank | ID | Priority | Queue state | Task | Evidence / Acceptance |
|---|---|---|---|---|---|
| Q1 | MET-WINDOW-C-01 | P1 Phase Gate | BLOCKED — FROZEN-PLAN-READINESS-RECORD (A reviewed FROZEN-PLAN READINESS RECORD exists before any collection night: frozen plan digest, issued calibration acceptance artifact, clean pinned head, empty waivers, fresh roots, and environment preflight, launcher-verified), ED-5A (Ed section-5A window prep FRESH POST-MOVE (the 2026-08-02 laptop move invalidated settled-machine conditions; network time off, AC, settled machine, walk-away)) | Execute a reviewed fresh-claim collection plan beginning with Window C: no Window B member enters a replacement claim basis; split prospectively across windows C and D if the complete replacement cannot fit the 2-4 hour envelope with at least 20 percent failure margin. | The fresh-claim metrology plan replaces every still-desired Window-B claim component without using any Window-B member, under reviewed frozen-plan and validated-window controls. Evidence: A fresh-claim plan recollects every still-desired Window-B claim component beginning with Window C; no Window B member enters a replacement claim basis; The fresh plan includes the still-required C2, C4, and C5 collection scope under the frozen-plan discipline, split prospectively across windows C and D if one window cannot retain at least 20 percent failure margin inside the runbook's 2-4 hour envelope; Window operated under the validated protocols: bird-SIGSTOP with identity custody, guarded launcher, one-line arm messages with zero output streaming during idle-gate exposure, third-failure salvage rule; Whole-window verdict emitted by machinery that has passed MET-VERDICT-ADJ-01 adjudication; supersessions recorded once, pre-verdict; both roots backed up rc=0. Authority: [D-113 clauses 7-9 fresh-claim reset, readiness fence, and prospective C/D split](docs/decision_log.md). Acceptance: [MET-WINDOW-C-01 acceptance](docs/process/state_kernel.json). Fence: A window-C dangler seeking the b-ii mechanical license before D100-BII-BINDING-01 closes RETURNS TO THE GATE; the window itself may run (D-106 revisit clause). Fence: Before any collection night, the ordinary launcher verifies a reviewed FROZEN-PLAN READINESS RECORD binding the frozen plan digest, issued calibration acceptance artifact, clean pinned head, empty waivers, fresh roots, and environment preflight (D-113 clauses 8-9 hard start fence). Fence: Plan root assembled and frozen before measurement; no plan edits after freeze (D-096 frozen-plan ratification). Fence: Zero agents AND zero operator output streaming during measurement idle gates; arm messages are one line; bird-SIGSTOP protocol with identity custody and fail-safe CONT trap on all exit paths (2026-08-01 run report: streaming-during-idle-gate hazard + bird-SIGSTOP protocol). Note: D-113 clauses 7 and 9: the former remainder-only scope is SUPERSEDED. A fresh-claim plan is required; no Window B member enters a replacement claim basis. If the full replacement exceeds the runbook's 2-4 hour envelope with at least 20 percent margin, split it prospectively across windows C and D. |
| Q2 | P2-006 | P2 Next Slice | READY | Homogeneous baselines (slice 2M) on the Mac target: Window A two-model campaign with drift-sentinel profiles, then docs/phase_2/baseline_results.md with variance plus prefill/decode comparison. | Strict-valid reducer-0.5.2/0.6.2 campaign bundles with counterbalanced order and drift sentinels; interpretation uses campaign claim_readiness plus the merged fail-closed analysis engine. Evidence: Strict-valid campaign bundles under the fixed validator; Counterbalanced order manifest + drift sentinel positions recorded; baseline_results.md with variance + prefill/decode comparison. Authority: [Phase 2 plan + analysis plans](docs/phase_2/phase_2_plan.md). Acceptance: [Phase 2 exit checklist](docs/phase_2/phase_2_exit_checklist.md). Note: Software interpretation gates are satisfied; Window-A floors landed 2026-07-31 (mint #1 mainline), so only the campaign remains. |
| Q3 | P2-010 | P2 Next Slice | READY | P2-010b remainder: affine smoke campaign execution (B=5) plus envelope-gate verdict on its bundles, on a quiet-window tail. | joulewise envelope-gate emits the D-036 verdict from strict-valid smoke bundles; campaign acceptance in AP-5. Evidence: D-036 verdict from strict-valid smoke bundles; AP-5 campaign acceptance met. Authority: [AP-5 + affine stream log](docs/contracts/analysis_plans.md). Acceptance: [P2-010 acceptance](docs/process/state_kernel.json). Note: Envelope-gate script merged 2026-07-09 (PR #23); only the campaign remains. |
| Q4 | P2-019 | P2 Next Slice | BLOCKED — P2-006 (Window-A baselines size n) | q4_l3_shape_grid_v1 campaign (Window B, AP-1, two models, n sized from Window A): 4x3 prompt/decode grid with holdouts (512,256) and (4096,512); categorical-additive fit first; 8192-prompt anchor on small+mid models feeding D-048 (CP-6). | Grid campaign lands per AP-1; top-up near-floor cells before L3 wording. Evidence: AP-1 grid campaign bundles; Holdout cells honored; 8192 anchor cells on small+mid models. Authority: [AP-1](docs/contracts/analysis_plans.md). Acceptance: [P2-019 acceptance](docs/process/state_kernel.json). |
| Q5 | P2-020 | P2 Next Slice | BLOCKED — P2-006 (Window-A baselines size n) | Content-sensitivity sentinel campaign (Window B, AP-6): five equal-shape ids-native conditions, n sized from Window A; request-energy deltas and MDE verdicts. | Campaign lands per AP-6; the AP-6 non-generalization caveat applies (D-046). Evidence: Five equal-shape ids-native conditions; Request-energy deltas + MDE verdicts. Authority: [AP-6 + D-046](docs/contracts/analysis_plans.md). Acceptance: [P2-020 acceptance](docs/process/state_kernel.json). Note: Generator merged (PR #19), manifests ready (PR #26); a tiny AP-6 pilot may ride a Window-A tail (CP-6). |
| Q6 | P2-012 | P2 Next Slice | BLOCKED — P2-006 (identification-core runs after Window A) | Identification-core campaign (jw_mixed) after Window A; natural-EOS pilot plus full panels in later phases. | Campaign bundles strict-valid per AP-4; no category claims outside matched strata. Evidence: Strict-valid bundles per AP-4; No category claims outside matched strata. Authority: [AP-4 + D-039/D-040](docs/contracts/analysis_plans.md). Acceptance: [P2-012 acceptance](docs/process/state_kernel.json). Note: Manifests generated + regenerated (PR #26); runner/runtime/validator hash guards merged (PRs #24/#27). |
| Q8 | P2-046B | P1 Phase Gate | READY | Execute the frozen load-transition alignment harness on the real Mac and adjudicate the production interval-support bound from offset and residual artifacts. | Real-Mac counterbalanced transitions validate or widen the P2-038 conservative interval-support bound; physical evidence replaces the PROVISIONAL Part-A verdict. Evidence: Counterbalanced real-Mac transition artifacts; Offset, residual, and conservative-bound verdict; P2-038 bound cited or amended. Authority: [Hardening adjudication C6](docs/reviews/2026-07-10-hardening-adjudication.md). Acceptance: [P2-046B acceptance](docs/process/state_kernel.json). Fence: Do not promote Part-A fixture evidence or retain PROVISIONAL interval support after a conflicting physical verdict (Hardening adjudication C6). Note: Part A merged in PR #50; Part B is quiet-machine physical execution. |
| Q9 | P2-047B | P2 Next Slice | BLOCKED — P2-047A (frozen controller-overhead harness exists) | Run the frozen controller capture-overhead ABBA on the quiet Mac and record the floor-governed overhead verdict. | Real floor-governed ABBA execution yields a named overhead verdict with instrumented-stack scope unless a separate subtraction model is justified. Evidence: Floor-governed quiet-Mac ABBA bundles; Named overhead verdict; Instrumented-stack scope or separately justified model. Authority: [Hardening adjudication C7](docs/reviews/2026-07-10-hardening-adjudication.md). Acceptance: [P2-047B acceptance](docs/process/state_kernel.json). |

### [AGENT] lane

| Rank | ID | Priority | Queue state | Task | Evidence / Acceptance |
|---|---|---|---|---|---|
| A0 | P2-035 | P3 Research Expansion | READY | RQ-ENERGY-VARIANCE promotion prerequisites: council round plus harness gaps G-RQVAR-* (per-bundle sampler seed recording, forced-token replay mode, replay manifests). | Promotion decided per registry rules; harness gaps closed before promotion. Evidence: Registry promotion record per docs/research_question_bank.md rules; G-RQVAR-* harness gaps implemented with tests. Authority: [RQ-ENERGY-VARIANCE candidate design](docs/specs/rq_energy_variance_design.md). Acceptance: [P2-035 acceptance](docs/process/state_kernel.json). Fence: C-004 quarantine binds; no promotion before floors exist (C-004 quarantine). |
| A2 | QUIET-GUARD-01 | P1 Phase Gate | READY; GATES live_promotion: T3-CHAR-PAIR-01 | Quiet-guard work order (full gauntlet): host-wide quiet lease, refuse-at-arm, characterized resident watcher; plus Ed requirements recorded 2026-08-03 — t3-armed operation (a t3-launched claude session arms a detached guarded chain, then self-quits and quits t3 with a survivor inventory), t3-relaunch-on-close, and README-banner signaling. | The quiet guard lands through the full C-028 gauntlet with the host-wide lease, refuse-at-arm, characterized resident watcher, and all three Ed-required t3 behaviors working end to end. Evidence: Commit 1 only: host-wide quiet lease implemented and enforced; Refuse-at-arm: arming refuses when the host is not quiet (usable by the ordinary guarded-shell window launcher); Installed-INACTIVE: no arming path, no production lease, live_promotion=false; Seven focused-audit blockers closed (priv-esc interpreter, validate/install TOCTOU, arbitrary-root initializer, macOS process identity, boot/hostname wedge, decision entry, independently-pinned tests); Full gauntlet on the landed commit: independent audit + delta re-audit of every fix round. Authority: [Ed directive 2026-08-03 ~23:55 (t3-drive chain is the critical path; non-in-flight work paused) + t3-doctrine gate synthesis + synthesis-exhibits SX5](docs/process_traces/2026-08-03-t3-doctrine-gate/SYNTHESIS.md). Acceptance: [QUIET-GUARD-01 acceptance](docs/process/state_kernel.json). Note: 2026-08-05: DESCOPED by Ed's directive (t3 control-plane build-out not worth its cost; t3 stays the INTERACTIVE control plane, t3-resident-during-windows dropped; windows return to the zero-agent guarded-shell path). ROW RE-SCOPED TO COMMIT 1 ONLY: the host-wide quiet lease + process census, installed-INACTIVE. Retained because it has non-t3 value — mechanical refuse-at-arm for the ordinary guarded window launcher, replacing procedural eyeballing. SHELVED: commit 2 (launcher interception), commit 3 (t3 handoff + resident watcher), commit 4 (t3-relaunch + README banner projection + all credential handling). In flight at checkpoint: Sol fix round closing 7 audit blockers; work UNCOMMITTED in scratchpad/quietguard (branch impl/quiet-guard); harvest scratchpad/qg-fix-out.md. |
| A3 | FLOOR-BIND-01 | P1 Phase Gate | READY | Bind canonical floor/MDE artifacts to governed extraction (CR9-1): authenticate admissible half-widths and complete campaign membership at claim consumption, with substitution/omission regressions. | Floor/MDE artifacts stop being self-attesting: claim consumption authenticates admissible widths and complete governed campaign membership against extraction evidence, retiring registered limitation L1. Evidence: Canonical floor cells bound to their extraction report and source-member disposition (or extraction gates and widths rederived at binding); Binding refuses on any stored width/corner mismatch or campaign-membership deviation; Integration regressions reject width substitution and member omission end-to-end. Authority: [D-078 clause 8 (confirmation round 9, registered limitation L1)](docs/decision_log.md). Acceptance: [FLOOR-BIND-01 acceptance](docs/process/state_kernel.json). Fence: Until this row closes, claim-bearing analysis may consume floor artifacts only from same-custody-session governed extraction; standalone artifacts are non-claim-bearing (D-078 clause 8 L1). Note: Minted 2026-07-22 from confirmation round 9 (CR9-1, lead-reproduced). L1 workflow rule mitigates until closed. |
| A4 | AXI-SB-ADAPTER | P2 Next Slice | READY | Implement the static-batch Mac adapter follow-on minted by the AXI-SB supported verdict: batch_size configuration knob, per-sequence request-scoped token events per the AXI-SA contract, realized-vs-configured batch recording, and structured memory-fit outcomes, with strict-valid mock or smoke bundles and no energy claims. | The follow-on static-batch adapter turns the AXI-SB supported verdict into an instrumented batch_size-configurable Mac runtime path emitting per-sequence AXI-SA events, with memory-fit failures structured and zero claim or quiet-Mac consumption. Evidence: A batch-capable Mac adapter exposes a batch_size configuration knob and emits per-sequence request-scoped token events conforming to the landed AXI-SA event contract, validated by strict bundle validation on a mock or live smoke bundle; Realized batch size is recorded alongside configured batch size, and structured memory-fit failures are captured as data rather than crashes; No energy claim, campaign scheduling, or quiet-Mac consumption occurs in this row; AP-BATCH execution remains separately floor-gated per AXI-SE. Authority: [AXI-SB verdict document (supported; mint-on-supported follow-on)](docs/specs/axi/sb_static_batch_verdict.md). Acceptance: [AXI-SB-ADAPTER acceptance](docs/process/state_kernel.json). Fence: Build on the verified BatchGenerator path with per-request observability; a Python loop over singleton calls is not a batch adapter (AXI-SB verdict document classification and scope). Fence: Keep continuous batching deferred and do not infer coalescing, scheduler-optimum, or offered-load claims from static-batch work (D-070 static-batch scope). Fence: Window A retains every quiet-Mac measurement slot; adapter implementation and mock or smoke validation are agent-lane work and consume no quiet-Mac campaign time (D-070 Window A ownership). |
| A5 | TEST-SPEED-01 | P2 Next Slice | READY | Cut suite wall-clock (three Ed-ratified levers, 2026-08-03): collect per-module timing data with the recovered profiling scripts, implement the shard-runner and the PR-fast/full tier split from the data, and evaluate Blacksmith runners. | The three Ed-ratified levers land: timing data drives a shard-runner plus PR-fast/full split with the full suite still holding every authoritative gate, and the Blacksmith runner option is evaluated on evidence. Evidence: Per-module timing corpus collected on a quiet bench (the recovered Sol profiling scripts; timings.jsonl + summary.json banked under .desk/) identifying the slow tail by module and by test; Shard-runner and the ratified PR-fast/full tier split implemented from the data: the fast tier gates PRs, the FULL suite remains the gate for merges, verdicts, and audited heads; zero test deletions; Blacksmith runner evaluation recorded with an adopt/defer recommendation and measured latency/cost comparison against GitHub-hosted runners. Authority: [Ed ratification 2026-08-03 (three levers: suite-speed priority, PR-fast/full split, Blacksmith runner evaluation); origin row in the 2026-07-28 report](docs/run_reports/2026-07-28-floor-mint-implementation.md). Acceptance: [TEST-SPEED-01 acceptance](docs/process/state_kernel.json). Fence: No test deletions, and the fast tier never substitutes for a required full-suite gate: merges, whole-window verdicts, and audited heads keep the full suite (D-061 zero-deletion clearance; the full suite as the authoritative gate). Note: 2026-08-03: timing DATA collected (quiet bench, 93 modules, 695s serial; raw in .desk/test-speed-consult/timings-20260803.jsonl) and DESIGN done (.desk/test-speed-consult/DESIGN-from-timing-data.md). Findings: suite is a 2-module problem (run_campaign 182s + p2038 133s = 45%); module-atomic sharding CAPS at 182s so those two must be split by TestCase class; shard-runner + splits -> ~87s wall @8 workers (6.5x); fast tier (drop 11 heavy integ modules) -> 25-40s PR feedback with the full suite still the merge gate. Blacksmith (lever 3) NEEDS ED (account/cost; likely marginal once sharded). Implementation queued: scripts/shard_tests.py + class-split + CI matrix — mechanical, delegatable, zero deletions (D-061). 2026-08-04: PHASE 1 LANDED — PR #98 MERGED (9b02539): module-atomic shard-runner + 8-way CI shard matrix, main CI green under it (~15min -> ~6min proven); worktree/branch pruned. Remaining scope: class-split of the two heavy modules (Phase 2), fast PR tier (lever 2), Blacksmith runners (lever 3, NEEDS ED). |
| A6 | AXI-SD | P2 Next Slice | READY | Prepare the matched dense/MoE pair proposal with the consult's pre-registered scorecard, including auditable active-parameter calculation and the D-016 cross-target 8 GB-fit question for Ed, plus a mirrored and hashed 2-to-3-level quantization ladder governed by C-023-QUALITY-EQUIV-QUANT. | A pre-registered matched dense/MoE selection scorecard and quantization ladder are artifact-complete before energy data, with active-parameter semantics explicit and the D-016 8 GB-fit choice surfaced to Ed. Evidence: A pre-data dense/MoE scorecard fixes family and tokenizer, runtime and quantization recipe, output policy, active-parameter calculation including shared experts and router top-k, artifact revisions and hashes, quality band, memory headroom, and fallback hierarchy; The scorecard surfaces to Ed whether D-016's cross-target 8 GB fit can be met or a separate Mac-only AXI pair or explicit D-016 amendment is needed; total-parameter fallback is labeled as a different estimand; A mirrored and hashed 2-to-3-level quantization ladder predeclares the C-023-QUALITY-EQUIV-QUANT identity and quality-equivalence gate before energy results. Authority: [AXI handoff work program S-D](docs/axi-handoff.md#4-work-program-post-audit-clearance-streams). Acceptance: [AXI-SD acceptance](docs/process/state_kernel.json). Fence: Do not silently substitute total-parameter matching for active-parameter matching; label the fallback as a different estimand and present the D-016 or separate-pair choice to Ed (Binding AXI xhigh consult). Fence: Prepare the pair proposal and scorecard but do not finalize D-016 or the Mac-only alternative without Ed (D-070 D-016 ownership). Fence: Window A retains every quiet-Mac measurement slot; AXI-SD is independent agent-lane desk and artifact work and consumes no quiet-Mac campaign time (D-070 Window A ownership). |
| A7 | AXI-SE | P2 Next Slice | READY | Finalize the AXI analysis plans after P2-015: AP-BATCH with counterbalanced all-B blocks, affine primary and lack-of-fit rule, structured B=16 memory outcome, and provisional n=5 under D-062; complete AP-SPEC and add AP-QUANT, AP-REASON-VARIANCE, AP-MOE-BATCH, plus the AP-5 dense/MoE 2M rider with the consult's floor and ownership closures. | The complete AXI analysis-plan family closes AP ownership for batching, speculation, quantization, reasoning variance, MoE-by-batch, and the AP-5 MoE rider with prospective floor, identity, multiplicity, model-fit, and structured-memory-outcome rules. Evidence: AP-BATCH freezes five counterbalanced all-B blocks over a fixed balanced equal-shape request roster, an all-B affine primary with predeclared lack-of-fit, an estimated-intercept interpretation, structured B=16 memory failure, latency bounds, and n=5 as provisional under D-062; AP-SPEC completion preserves S-A's gross request and committed-output primary denominators, accepted-draft diagnostic, exact-token identity gate, separate MTP and draft families, floor mapping, pairing, multiplicity, and divergence dispositions; AP-QUANT, AP-REASON-VARIANCE, AP-MOE-BATCH, and the AP-5 MoE 2M rider close the all-axis ownership gap, with routing-mechanism claims allowed only when auditable expert evidence exists and every plan finalized only against P2-015 floors. Authority: [AXI handoff work program S-E](docs/axi-handoff.md#4-work-program-post-audit-clearance-streams). Acceptance: [AXI-SE acceptance](docs/process/state_kernel.json). Fence: Do not promise a confirmatory breakpoint or fixed n=5 before floors; freeze all-B affine lack-of-fit, final n, floor transport, multiplicity, and forbidden upgrades prospectively (Binding AXI xhigh consult). Fence: Keep every plan at or below L2 and preserve static-batch scope, exact claim boundaries, and structured unsupported or not-resolvable outcomes (D-070 all-axis claim posture). Fence: Window A retains every quiet-Mac measurement slot; AXI-SE is agent-lane analysis-plan finalization after P2-015 and authorizes no measurement campaign by itself (D-070 Window A ownership). |
| A10 | SUPERSESSION-DUP-REFUSAL-01 | P1 Phase Gate | READY | Rule on and then implement write-time refusal in the supersession recorder, which today appends silent duplicate records when run more than once for a member and voids campaign membership downstream; the ruling is the first half of the deliverable. | A repeat recorder invocation for the same member refuses instead of appending a duplicate record. Evidence: The write-time refusal ruling is recorded in the decision log before any implementation; A regression asserts that a second recorder invocation for the same member refuses. Authority: [D-086 supersession-aware cooldown-evidence join (recorder duplicate-append defect)](docs/decision_log.md). Acceptance: [SUPERSESSION-DUP-REFUSAL-01 acceptance](docs/process/state_kernel.json). Fence: Until the refusal lands, run the supersession recorder exactly once per member (D-086 operator mitigation). Note: Minted 2026-07-30 from the D-086 arc; ruling-first, no implementation before it. |
| A11 | T3-PROV-SCHEMA-01 | P2 Next Slice | READY | Implement the tracked four-axis provenance record with authority_class and the ingestion-event schema, then make reverse-consult admission consume authoritative launch-route and owner_kind evidence so bridge §8's transitional convention ends. | The four-axis provenance plus ingestion-event schema ends bridge §8's transitional convention by mechanically enforcing reverse-consult eligibility from authoritative route and ownership evidence. Evidence: A tracked provenance record represents the four axes control_plane, transport, authority_class, and governance, with authority_class explicit; A tracked ingestion-event schema binds native session identity, output digest, lead disposition, and tracked process-trace location; Reverse-consult admission consumes authoritative launch-route and owner_kind evidence rather than self-reported headers; Rejection regressions fail closed on delegated, unknown, or contradictory provenance and prove that merely persisting the schema cannot end the transition. Authority: [Bridge protocol §8 transitional reverse-consult enforcement follow-on](docs/contracts/bridge_protocol.md). Acceptance: [T3-PROV-SCHEMA-01 acceptance](docs/process/state_kernel.json). Fence: The transition ends only when admission consumes authoritative launch-route and owner_kind evidence with rejection tests; defining or persisting the schema alone is insufficient (Bridge protocol §8 fail-closed transition rule). Note: Bridge §8 currently validates only self-reported headers; consumption-side fail-closed is the actual protection until this row supplies real enforcement. |
| A12 | MINT-GENERALIZE-01 | P1 Phase Gate | BLOCKED — D-110 (The remaining D-110 re-mint conditions hold before ANY further mint, including the governed 7B mint: (b) the acceptance artifact is ISSUED after verified R2 backfill and deterministic ledger bootstrap; (c) the evidence_root_id validator pin is widened) | Generalize the mint beyond the mint-1 pair: scripts/mint_floor_artifact.py is hard-pinned to the p2_015, a10, and window-C evidence (cell id, plan sha, both order-manifest ids, the two member counts, the expected operative-floor text), so build a sibling taking those pins per plan and carrying the 7B mint's remaining scope. | A generalized mint sibling takes the mint-1 hard pins per plan so a second floor artifact can be minted without weakening the pre-registration gate. Evidence: A 7B decode-floor artifact mints from qwen25_7b_decode_floor_v1 evidence with its own hard six-decimal operative-floor literal supplied per plan, never derived inside the mint path; The pre-registration gate passes as-embedded and validate_floor_artifact returns no findings; The generalized path mints byte-identical to the reviewed core from the same inputs on the same integration tree (core-vs-wrapper parity per D-109 addendum II; NOT a match against historical mint-1 digests, which D-110's corrected re-mint may legitimately change). Authority: [splitwise_decode_v1 campaign doc section 2 Blocker A (mint pins); D-082, D-084, D-085 Q6](docs/phase_2/splitwise_decode_campaign.md). Acceptance: [MINT-GENERALIZE-01 acceptance](docs/process/state_kernel.json). Fence: Generalize the plumbing, never the pins: six-decimal floor literals and lead-verified digests stay supplied per plan and hard-checked in-tool (D-082 and D-084 operative-floor pins). Note: 2026-08-03: D-110 (sweep finding RT-1/RT-2): mint #1 is retroactively NON-CLAIM-BEARING (taint-and-remint); the night consult's conditional 7B-mint license is SUSPENDED. The mint-1 byte-compare replay completed BYTE-IDENTICAL at pinned 3de370ec (all four digests; docs/process_traces/2026-08-03-q1-remint-bytecompare/). 2026-08-05: condition (a) is satisfied by merged PR #100. Condition (b) preparation is complete and its verification blocker is resolved: the B1 disposition is lead-ruled 30/2/6 and deterministic bootstrap is implemented on impl/ledger-bootstrap, under audit. Condition (c) is in flight on impl/validator-rootpins. The row remains hard-blocked on the still-pending D-110 (b)+(c) completion gate. |
| A13 | CODEX-BRIDGE-SANDBOX-01 | P2 Next Slice | READY | Correct scripts/codex-bridge review-mode sandbox enforcement: pass the read-only sandbox flag instead of launching workspace-write while recording read-only metadata. | codex-bridge review launches read-only exactly as its audit manifest claims, with regression coverage binding recorded and effective sandbox values. Evidence: scripts/codex-bridge review passes the read-only sandbox flag to every non-app review launch; The review audit manifest records the sandbox actually supplied to the launch; A regression proves the recorded review sandbox and launched sandbox are both read-only and cannot drift apart. Authority: [2026-08-05 live inspection: review records observer_sandbox=read-only but the non-app launch omits -s read-only](scripts/codex-bridge). Acceptance: [CODEX-BRIDGE-SANDBOX-01 acceptance](docs/process/state_kernel.json). Note: Caught live 2026-08-05: observer_sandbox is set to read-only, but the non-app review invocation omits the sandbox flag, so audit metadata misstates enforcement. |
| A14 | COLDGATE-HANDOFF-01 | P2 Next Slice | READY | Build runner-owned sealed-byte judge handoff: capture immutable in-process packet, charter, and exhibit byte snapshots; compute digests over those exact buffers; construct judge input from the same buffers; and specify and test transport byte-to-request binding. | The convening runner delivers exactly the bytes the validator observed, with immutable snapshot-to-judge transport binding and a judge-identity-bound runner receipt. Evidence: Deterministic post-hash path replacement delivers the original immutable snapshot or refuses without invoking the judge; Same-inode mutation through a second descriptor never delivers mutated bytes under the old receipt; Judge-received payload hashes equal the receipt hashes and the runner receipt binds the judge request or session identity. Authority: [2026-08-05 COLDGATE-VALIDATOR F3 consult Q2 handoff ruling and tests](docs/process_traces/2026-08-05-cgv-f3-consult/CONSULT-REPORT.md). Acceptance: [COLDGATE-HANDOFF-01 acceptance](docs/process/state_kernel.json). Fence: Until this row lands, no validator PASS may be used to convene a cold judge (2026-08-05 F3 consult standing operational constraint). Note: Design warnings: holding file descriptors open does NOT seal bytes because a second descriptor can mutate the same inode; path-based launch-time revalidation alone leaves a revalidate-to-read race. Pending-ratification payload carried by this row: the proposed amendment to docs/process/coldgate_charter_registry.md separating validator observation from runner custody. The registry is Ed-ratified and is NOT edited by this or any session without a cold-gate/Ed ratification. |
| A15 | C3-RECOGNIZER-EXACT-01 | P1 Phase Gate | READY | Close the two D-105-registered recognizer-exactness blockers: exact escape-ordering completion-feasibility (F1) and the documented decidable superset number grammar (F2, with the D-104 cl.2 subset-direction amendment), plus the bundled F3/N2 release-path hygiene if not already landed. | The two registered recognizer-exactness blockers (escaped-key ordering; number-prefix over-acceptance) close together under D-105's refuter-amended criteria with an independent audit. Evidence: F1 closes via the exact escape-ordering completion-feasibility procedure (hex-digit interval derivation, surrogate-pair arithmetic, prefix-extension rule) with both registered counterexamples pinned verbatim and a BMP/non-BMP boundary property test; F2 closes via a DOCUMENTED DECIDABLE SUPERSET grammar of json.dumps float spellings (fixed-notation exponent window, coefficient rules, two-digit exponent padding) — the D-104 cl.2 subset direction is amended per D-105 to 'accepted within the documented superset AND containing every real writer prefix'; both counterexamples refuse; randomized-float completeness property passes; Both registered blockers close together with an independent delta audit at the exact head; the acceptance-set contract re-proven in both amended directions over a corpus including non-BMP keys. Authority: [D-105 disposition synthesis (F1/F2 registered as a NEW ruling, not D-088 precedent; closure criteria refuter-amended; number-grammar exactness struck)](docs/decision_log.md). Acceptance: [C3-RECOGNIZER-EXACT-01 acceptance](docs/process/state_kernel.json). Fence: F1/F2 severity may not be downgraded by any role; closure ONLY through this row; while open the recognizer's accepted set may only SHRINK; the custody sidecar and writer-side ASCII key assertion (the D-105 micro-commit) are load-bearing compensating controls and may not be weakened (D-105 registration fences). Fence: This registration must not be cited as precedent for registering corpus-absent defects generally; it is a new ruling made with three recorded independent absence scans and mechanical compensating controls (D-105: branch-introduced registration is NOT QA-10A/B precedent). |
| A16 | P3-000 | P3 Research Expansion | BLOCKED — R-003 (user approves the 3.0.2 installs (R-003)) | KV persistence feasibility spikes (Phase 3 Stage 3.0): 3.0.2+ open; 3.0.2 needs installs and inherits the 3.0.1 harness shape plus its two deferred hardening fixes (ledger C-8). | Verdicts recorded in docs/phase_3/kv_feasibility.md; checklist rows are the status authority; must complete before any borrow-window scheduling. Evidence: Verdicts in docs/phase_3/kv_feasibility.md; Checklist rows updated. Authority: [D-035/D-036](docs/decision_log.md). Acceptance: [Phase 3 exit checklist](docs/phase_3/phase_3_exit_checklist.md). Note: 3.0.1 complete and merged (PR #9, replay_supported). |
| A17 | P2-022 | P2 Next Slice | BLOCKED — P2-006 (the 2M corpus exists (post-2M per D-041)) | Marker-shim energy-layer feasibility spike: verdict-shaped export path only (external_markers_supported / partial / external_markers_unsupported). | 3+ marked items, external result artifact hashed, strict bundle valid; verdict recorded. Evidence: 3+ marked items; External result artifact hashed; Strict bundle valid. Authority: [D-041 (post-2M gate)](docs/decision_log.md). Acceptance: [Adapter contract](docs/contracts/adapter_contracts.md). Fence: Energy-layer-only pin: no accuracy interpretation, no leaderboard join, no pass@k-energy ratio, no general adapter framework; AP row required before any L2 claim (D-041). Note: C-027: the C-026 revisit-after-Window-A note is a revisit of sequencing, not permission. |
| A18 | P2-023 | P2 Next Slice | BLOCKED — P2-006 (the 2M corpus exists (post-2M per D-041)), P2-022 (P2-022 verdict recorded) | HumanEval import smoke: benchmark_import manifest plus suite profile plumbing goal; freeze subset with C-005 discipline, MIT license/provenance fields, 256/512-token completion policy. | Frozen subset with license/provenance fields lands; no pass@k/accuracy/capability claim. Evidence: Frozen subset manifest with C-005 discipline; License/provenance fields present. Authority: [D-041 (post-2M gate)](docs/decision_log.md). Acceptance: [RQ bank import-smoke design](docs/research_question_bank.md). Fence: No pass@k, accuracy, or capability claim (D-041). |
| A19 | P2-024 | P2 Next Slice | BLOCKED — P2-006 (2M reductions identify floor/MDE headroom) | Cheap-campaign shortlist: select among C5-1.6 sampler ABBA, C5-1.12 quant decomposition, C5-1.8 runtime attribution per measured floors; the selected campaign is then queued [QUIET-MAC]. | Explicit selection recorded after floors; selection cites floor/MDE headroom. Evidence: Selection recorded with floor/MDE headroom rationale; Selected campaign queued as a quiet_mac task. Authority: [C-015 + RQ bank](docs/research_question_bank.md). Acceptance: [P2-024 acceptance](docs/process/state_kernel.json). |
| A21 | P3-001b | P3 Research Expansion | BLOCKED — P2-006 (2M affine coefficients exist) | Seed the split analysis-plan row: pre-registered compositional predictions per pairing/link (including named same-boundary headline and at least one predicted-crossover cell if feasible), per-cell transfer-boundary labels (D-049). | AP row committed before any split hardware run; phase_3_plan amendment line landed. Evidence: AP row committed pre-split-hardware; phase_3_plan amendment line landed. Authority: [D-048/D-049](docs/decision_log.md). Acceptance: [Analysis plans (split row)](docs/contracts/analysis_plans.md). |
| A22 | P2-004 | P2 Next Slice | PARTIAL; READY; GATES close: P1-001 | Close model selection (D-016): decision-log entry with models, revisions, artifact paths, local mirror, fallback candidate; mid-model pick, CUDA load, GGUF paths outstanding. | Decision-log entry complete; full closure gated on P1-001. Evidence: Decision-log entry: models, revisions, artifact paths, mirror, fallback. Authority: [D-016](docs/decision_log.md). Acceptance: [Phase 1 exit checklist](docs/phase_1/phase_1_exit_checklist.md). Note: Provisional small-model pick 2026-07-06 opens 2G. |
| A23 | P2-005 | P2 Next Slice | PARTIAL; READY; GATES live_promotion: P1-006 | Remote targets (2K NVIDIA/vLLM/ssh and 2L Orin): fixture-first and NV-GATE-2 code-now hardening are merged; protocol pins remain provisional until the external live-promotion rows execute. | Live 2K/2L evidence or a documented access blocker; applicability table updated; NV-GATE-2 live rows close without promoting fixture evidence. Evidence: Remote bundle or documented access blocker; Applicability table updated; NV-GATE-2 items closed at live promotion. Authority: [NV-GATE-2 live-promotion spec](docs/specs/c027/nv-gate-2_live_promotion.md). Acceptance: [2K live verification checklist](docs/phase_1/2k_live_verification_checklist.md). Note: PR #49 merged the code-now verifier, streaming, cleanup, and localhost gates; P1-006 and device execution remain open. |
| A24 | P2-016 | P2 Next Slice | BLOCKED — P2-006 (the 2M corpus exists) | Critique-adjudicated queue batch (umbrella a..i): post-2M controller split; node-worker protocol parity tests; NVIDIA skip counts into measurement quality; per-backend raw-to-trace strict generalization; claims-to-evidence index post-2M; schema v0.2 loader/export parity; boundary labels in report index; summary_provenance strict key; token_count_source naming alignment. | Each item lands with its named gate; dispositions plus rejected items recorded in C-011. Evidence: Each subitem lands with its named gate; Dispositions recorded in C-011. Authority: [C-011 ledger + C-027 (post-2M umbrella)](docs/reviews/2026-07-09-c027-whole-project-review.md). Acceptance: [P2-016 acceptance](docs/process/state_kernel.json). Note: Stage 1 conservatively blocks the parent; a later owning session may split P2-016a..i through normal intake. |
| A25 | P2-047A | P2 Next Slice | READY | Freeze the controller capture-overhead ABBA harness comparing the standard event path with a buffered or minimal-marker path under identical outputs and hashes. | A frozen controller-overhead ABBA harness preserves output identity and defaults to instrumented-stack scope rather than unvalidated subtraction. Evidence: Frozen ABBA manifest; Standard and buffered/minimal-marker paths have identical output policy and hashes; Analysis refuses unsupported subtraction. Authority: [Hardening adjudication C7](docs/reviews/2026-07-10-hardening-adjudication.md). Acceptance: [P2-047A acceptance](docs/process/state_kernel.json). Fence: Do not subtract controller overhead without a separately justified correction model (Hardening adjudication C7). |
| A29 | DOC-008-REFLECTION | P4 Polish | READY | Replace planning_reflection_protocol.md with the DOC-008 redirect stub and reconcile its inbound references under condition 6. | Retire the reflection protocol as an independent intake surface while preserving its compatibility path. Evidence: planning_reflection_protocol.md is the exact redirect stub; Useful fields remain owned by the kernel or run reports; Inbound references use the consolidated intake route. Authority: [DOC-008 reflection-protocol retirement](docs/specs/c027/doc-008_state_kernel.md). Acceptance: [DOC-008 reflection-protocol retirement](docs/specs/c027/doc-008_state_kernel.md). Fence: Keep the compatibility path and do not create another intake checklist (DOC-008 reflection-protocol fence). |
| A30 | DOC-008-STATUS | P4 Polish | READY | Perform the lead-authored PROJECT_STATUS compaction and verbatim history archival required by DOC-008 condition 8. | Lead compacts PROJECT_STATUS and preserves removed dated updates in the specified history archive. Evidence: Lead-authored PROJECT_STATUS has at most seven current sections; Removed dated updates are preserved verbatim in the history archive; Advisor-visible quantitative claims retain evidence pointers. Authority: [DOC-008 PROJECT_STATUS compaction](docs/specs/c027/doc-008_state_kernel.md). Acceptance: [DOC-008 PROJECT_STATUS compaction](docs/specs/c027/doc-008_state_kernel.md). Fence: Lead authors final advisor-facing claims and no generator writes PROJECT_STATUS (DOC-008 PROJECT_STATUS authorship fence). |
| A31 | DOC-008-INTAKE | P4 Polish | READY | Reconcile agent_playbook, AGENT_PLAN, README, orchestration, and remaining intake text with the generated kernel route in DOC-008 conditions 4 and 9. | Reconcile the remaining intake and procedure surfaces without creating another live-state mirror. Evidence: M0 is the sole short intake owner; Inbound procedure references no longer conflict; Generated regions remain the only work-selection views. Authority: [DOC-008 intake and procedure reconciliation](docs/specs/c027/doc-008_state_kernel.md). Acceptance: [DOC-008 intake reconciliation](docs/specs/c027/doc-008_state_kernel.md). Fence: Do not add hand-maintained ranked next-work or phase-completion mirrors (DOC-008 intake reconciliation fence). |
| A32 | DOC-008 | P4 Polish | PARTIAL; READY; GATES close: DOC-008-INTAKE; GATES close: DOC-008-REFLECTION; GATES close: DOC-008-STATUS | Close the reopened DOC-008 migration only after residual conditions 4, 6, 8, and 9 land and every original completion condition is rechecked. | Every original DOC-008 completion condition lands before the reopened task returns to complete. Evidence: All nine DOC-008 required outcomes rechecked; Focused and canonical suites pass; Final-head review confirms one work-selection authority. Authority: [DOC-008 state-kernel specification](docs/specs/c027/doc-008_state_kernel.md). Acceptance: [DOC-008 required outcomes](docs/specs/c027/doc-008_state_kernel.md). Fence: Do not redeclare DOC-008 complete until every original required outcome lands (DOC-008 required outcomes). Note: Reopened by WO-021; phase C repairs work-selection authority while three residual task records remain live. |
| A33 | P2-050 | P3 Hardening Candidates | READY | Adjudicate the C-028 dissent-record candidates separately: frozen-legacy claim_eligibility mapper, semantic cooldown-row verification, once-per-manifest first-run exemption, scoped top-up detection, and cooldown trace v2. | Each C-028 dissent-record candidate receives its own adjudication before any implementation. Evidence: Frozen-legacy claim_eligibility mapper receives its own adjudication; Semantic cooldown-row verification receives its own adjudication; Once-per-manifest first-run exemption receives its own adjudication; Scoped top-up detection and cooldown trace v2 receive their own adjudications. Authority: [C-028 dissent-record queue candidates](docs/run_reports/2026-07-11-c028-continuation.md). Acceptance: [P2-050 acceptance](docs/process/state_kernel.json). Fence: Do not implement any candidate before its own recorded adjudication (C-028 dissent-record queue candidates). |
| A34 | TOOL-01 | P3 Tooling | READY | Fix codex-run-v3 defects: resume-after-NEEDS_SCOPE no-op; preventive permission profiles; NEEDS_RULING recognition; effort-default passthrough; stream-death OK exits with thin out-files; resume --last cross-thread attachment through the global latest session; and session-open paths lacking per-path match specifiers. | All seven codex-run-v3 defects close in lead personal tooling with targeted regressions and updated adapter operations lessons. Evidence: Resume after NEEDS_SCOPE continues the requested work; Preventive permission profiles and NEEDS_RULING recognition are covered; Omitted effort defaults to xhigh instead of config passthrough; Upstream stream death fails instead of exiting OK with a thin out-file; Resume requires an explicit session ID and cannot cross-attach through a global --last pointer; Session-open accepts a per-path match specifier without post-hoc child expansion. Authority: [Bridge v1.1 wrapper and session operations record](docs/run_reports/2026-07-13-bridge-v11.md). Acceptance: [TOOL-01 acceptance](docs/process/state_kernel.json). Fence: Keep implementation in lead personal tooling; this repository owns only the work record (Bridge v1.1 wrapper and session operations record). Note: lead personal tooling, non-repo |
| A35 | AUD-FOLLOWUPS | P3 Hardening Candidates | READY | Close the ULTRA comparison audit's accepted small residue in one bounded agent task: WO-012's owned D-062 lint queue row, WO-014 realized-token discrimination, WO-017 default no-handoff regression, WO-020 standalone bridge-checker decision, and WO-040 authored-instruction absolute-path plus genuine pristine-clone coverage. | The ULTRA comparison audit's five accepted small follow-ups close with discriminating tests or an explicit recorded decision, without creating a ceremony-dispositions task. Evidence: WO-012's owned D-062 lint queue-row obligation is implemented and covered; WO-014 has a realized-token discriminating test; WO-017 has a default no-handoff regression assertion; WO-020 has a recorded standalone bridge-checker decision; WO-040 has authored-instruction absolute-path coverage plus a genuine pristine-clone test. Authority: [Comprehensive-audit close-out and accepted-residue list](docs/reviews/2026-07-13-comprehensive-audit/report.md). Acceptance: [AUD-FOLLOWUPS acceptance](docs/process/state_kernel.json). Fence: Do not create AUD-CEREMONY-DISPOSITIONS; ceremony dispositions remain report-owned (Comprehensive-audit report disposition ledger). Note: Accepted small residue only; audit ceremony dispositions remain in the report. |
| A36 | AUD-WO-033 | P3 Hardening Candidates | READY; GATES close: P2-006 | After 2M, split scripts/run_campaign.py along tested policy seams, pure validation and provenance first and execution lifecycle second, only when campaign-scale or split or multi-node work first forces edits to that path. | The post-2M campaign-runner refactor is behavior-preserving across the full campaign test portfolio and retains every collection and claim-readiness safeguard. Evidence: Pure validation and provenance seams are extracted before execution lifecycle seams; The full campaign behavior-parity portfolio is green before and after the split; Locks, waivers, backups, cooldown, and claim-readiness behavior remain unchanged. Authority: [Comprehensive-audit register WO-033](docs/reviews/2026-07-13-comprehensive-audit/register.jsonl). Acceptance: [Comprehensive-audit register WO-033](docs/reviews/2026-07-13-comprehensive-audit/register.jsonl). Fence: Keep this post-2M and behavior-preserving; do not redesign campaigns or weaken locks, waivers, backups, cooldown, or claim-readiness gates (Comprehensive-audit register WO-033 non-goals and risk note). |
| A37 | AUD-WO-034 | P3 Hardening Candidates | READY; GATES close: PHASE-3-SPLIT-SCHEDULED | At Phase-3 split scheduling, assign bounded owners and dependencies for transfer-bench, split replay, composite validate and reduce, KV-economics reduction, and matrix-generator extension before any PLANNED command becomes executable. | When Phase-3 split work is scheduled, every PLANNED pack command gains an owner or explicit deferred marker without pack collapse or premature implementation. Evidence: Every PLANNED command has a bounded owner row or explicit deferred-design marker; Pack-command ownership lint passes positive and negative fixtures; Settled split pre-registration requirements and offline-before-live fences remain intact. Authority: [Comprehensive-audit register WO-034](docs/reviews/2026-07-13-comprehensive-audit/register.jsonl). Acceptance: [Comprehensive-audit register WO-034](docs/reviews/2026-07-13-comprehensive-audit/register.jsonl). Fence: Do not prune draft designs, collapse campaign packs, or implement split or KV work in this ownership pass (Comprehensive-audit register WO-034 non-goals). |
| A38 | AUD-WO-035 | P3 Hardening Candidates | READY; GATES close: 2K-LIVE-REMOTE-TRANSFER-SCHEDULED | Before the first 2K-live or remote split-transfer task, define a versioned discriminated node-worker payload and test realistic typed rejection without overloading telemetry blocks. | The 2K-live and remote roadmap has a versioned transfer-task payload seam with typed rejection before split-transfer implementation. Evidence: A versioned discriminated payload path exists for transfer tasks; A realistic unsupported transfer request fails with a typed versioned error; Telemetry blocks are not overloaded with transfer semantics. Authority: [Comprehensive-audit register WO-035](docs/reviews/2026-07-13-comprehensive-audit/register.jsonl). Acceptance: [Comprehensive-audit register WO-035](docs/reviews/2026-07-13-comprehensive-audit/register.jsonl). Fence: Define and reject the future transfer shape only; do not implement split execution or transfer benchmarking (Comprehensive-audit register WO-035 non-goals). Note: D-043 supersession closure falls due at landing: add the dated protocol-version supersession line identified by PA-2. |
| A39 | AUD-WO-036 | P3 Hardening Candidates | READY; GATES close: 2K-LIVE-REMOTE-CONCURRENCY-SCHEDULED | When 2K-live or remote retries or concurrency are introduced, add a pre-launch node and GPU ownership lease plus idempotent duplicate prepare and start behavior. | Retries or concurrent 2K-live and remote campaigns cannot double-own a node or GPU and duplicate delivery is idempotent. Evidence: Duplicate prepare and start delivery is idempotent; Node and GPU ownership is leased before launch; Concurrency coverage exercises the ownership and duplicate-delivery contract. Authority: [Comprehensive-audit register WO-036](docs/reviews/2026-07-13-comprehensive-audit/register.jsonl). Acceptance: [Comprehensive-audit register WO-036](docs/reviews/2026-07-13-comprehensive-audit/register.jsonl). Fence: Do not run concurrent hardware campaigns or make live-correctness claims in this agent task (Comprehensive-audit register WO-036 non-goals). |
| A40 | AUD-WO-037 | P3 Hardening Candidates | READY; GATES live_promotion: 2K-LIVE-PROMOTION-SCHEDULED | Fold non-self-asserted promotion authority into the 2K-live P2-005 and NV-GATE-2 code-now path before live promotion: bind an implementation receipt to commit and protocol pins and derive per-bundle execution class from the transport path. | Before 2K live promotion, non-self-asserted implementation authority and transport-derived execution classification fail closed at claim admission. Evidence: Fixture, unknown, unpromoted-live, and promoted-live classifications are tested; Unknown and unpromoted NVIDIA bundles are refused at claim admission; Promotion receipt is commit and protocol bound and cannot be forged through config or metadata. Authority: [Comprehensive-audit register WO-037](docs/reviews/2026-07-13-comprehensive-audit/register.jsonl). Acceptance: [Comprehensive-audit register WO-037](docs/reviews/2026-07-13-comprehensive-audit/register.jsonl). Fence: Land this before, never after, the first claim-bearing NVIDIA live promotion; do not execute NV-GATE-2 or de-provisionalize hardware results here (Comprehensive-audit register WO-037 non-goals). Note: D-043 supersession closure falls due at landing: add the dated D-057 governed-reason amendment identified by PA-2. |
| A41 | AUD-WO-038 | P3 Hardening Candidates | READY; GATES close: 2K-LIVE-REMOTE-MULTINODE-DECIDED | At the 2K-live or remote multi-node roadmap decision, choose one owned remote execution boundary, consolidate duplicated lifecycle evidence helpers, and remove only proven-unconsumed transport surface with compatibility disposition. | At the 2K-live or remote multi-node decision, one owned execution boundary replaces only proven duplication while node-worker safeguards and public compatibility remain intact. Evidence: Lifecycle parity covers node-worker, subprocess, SSH, interface, and controller failure paths; Every deleted surface has a bounded absence or deprecation-compatibility trace; node_worker remains self-contained with backend-specific timeout, identity, log, clock, and cleanup safeguards. Authority: [Comprehensive-audit register WO-038](docs/reviews/2026-07-13-comprehensive-audit/register.jsonl). Acceptance: [Comprehensive-audit register WO-038](docs/reviews/2026-07-13-comprehensive-audit/register.jsonl). Fence: Re-baseline against WO-001 and WO-010, keep node_worker self-contained, and do not delete public transport methods on repository absence alone (Comprehensive-audit register WO-038 risk boundaries). Note: D-043 supersession closure falls due at landing: back-annotate the public adapter and transport contract as required by PA-2. |
| A42 | AUD-WO-039 | P3 Hardening Candidates | PARTIAL; READY; GATES close: SITE-CAPACITY-RIGHTSIZING-DECIDED | At the next explicit site-capacity or right-sizing decision after SITE-02, remove only proven-unused live payload fields and make any further page trim through a recorded retained-route and value-versus-bytes review. | The remaining site payload and right-sizing work removes only proven-unused live fields and any page removal follows an explicit value-versus-bytes retention review. Evidence: Packed-byte and request reduction is measured; Route and link checks pass and every removed page has a retention decision; Consumed views, deep links, source access, and provenance stamps remain intact. Authority: [Comprehensive-audit register WO-039](docs/reviews/2026-07-13-comprehensive-audit/register.jsonl). Acceptance: [Comprehensive-audit register WO-039](docs/reviews/2026-07-13-comprehensive-audit/register.jsonl). Fence: Trim only live payload fields proven unused; preserve advisor-facing pages, navigation, source access, stable deep links, and provenance unless a per-page retention review says otherwise (Comprehensive-audit register WO-039 preservation boundary). Note: Partial page trim landed 2026-07-15 by redirecting the duplicative capsule task-queue mirror while preserving its routes; remaining payload work is open. D-043 supersession closure falls due at landing through the dated D-051 amendment identified by PA-2. |
| A43 | CUSTODY-HARDEN-01 | P2 Next Slice | READY | Custody hardening follow-on from the screen+budget gauntlet: reduce-layer label-trust removal (G2A), drift-bound seal authentication (A3-r2), dead no-freshness accommodation disposition, artifact_schema_invalid mislabel. | Close the PR #85 gauntlet's deferred custody-hardening seams: config-derived mockness reaches the reduce-layer barriers, the drift-bound seal stops being self-certifying, and two diagnostic nits are resolved. Evidence: Reduce-layer environment/CPU claim barriers derive mockness from the custody-bound config, with metadata/summary-label early returns removed; Drift-bound artifact corpus identities resolve against repo-registered or custody-bound bytes (seal no longer self-certifying); Dead pre-addendum no-freshness accommodation removed or pinned as intentional forward-compatibility; artifact_schema_invalid evidence-binding mislabel renamed or documented at emission site. Authority: [C-045 gauntlet deferrals (council log; detail in docs/run_reports/2026-07-24-screen-budget-gauntlet.md)](docs/council_log.md). Acceptance: [CUSTODY-HARDEN-01 acceptance](docs/process/state_kernel.json). Note: Minted 2026-07-25 from PR #85 gauntlet deferrals; triangle-agreement enforcement (merged) already raises these seams to three-file forgery cost. |
| A46 | FLOOR-WORKLOAD-SIZING-01 | P1 Phase Gate | READY | Re-size the floor/science campaign workloads so measured effects clear the duration-independent attribution floor, and pilot the resulting effect-to-floor ratio before spending quiet-machine nights on ABBA collection at current sizes. | Anchor-attribution error is approximately duration-independent (~1 J regardless of phase size) while effects scale with workload, so lengthening prefill/decode raises effect-to-floor linearly at zero instrument cost. Evidence: Measured effect-to-floor ratio at candidate workload sizes, from a pilot rather than assumption; Re-sized configs for the remaining floor stages, with the sizing rationale recorded; Explicit decision on which queued stages are collected at which sizes. Authority: [2026-07-25 attribution-limit adjudication (Fable ruling + Sol replay; plan in session scratchpad)](docs/decision_log.md). Acceptance: [FLOOR-WORKLOAD-SIZING-01 acceptance](docs/process/state_kernel.json). Note: Minted 2026-07-25; scope corrected same day after the quantitative replay. NOT a blocker on the ABBA roadmap: under the labelled-floor path the queued stages remain scientifically viable at current sizes (tens-of-percent effects on ~50 J clear a ~3 J floor plus claim-side bound). This is a MARGIN optimisation — attribution error is duration-independent while effects scale with workload, so longer prefill/decode buys effect-to-floor ratio for free. Pilot the ratio at candidate sizes before committing the remaining quiet-machine nights. |
| A47 | FLOOR-COMMONMODE-01 | P2 Next Slice | READY | Pre-register and evaluate a common-mode anchor estimator for ABBA blocks: sweep one shared fiducial shift across all four members, re-integrate measured curves, and add only genuinely per-bundle components adversarially. | The fiducial term is ~80% of the composed anchor bound (24.9 of ~31.1 ms, verified) and is literally the same artifact for all four members of a block; treating it as four independent adversarial draws is itself an unphysical modelling choice. Evidence: Block-timescale fiducial stationarity registered as a NAMED transfer assumption with its evidence; Estimator pre-registered before it touches claim-bearing data; The identical estimator applied to BOTH the calibration blocks and the consuming science contrast (a floor calibrated with cancellation the consumer does not get would understate false effects); Quantified gain on a5/a10 blocks versus the worst-case-sum default. Authority: [2026-07-25 attribution-limit adjudication (Fable ruling + Sol replay; plan in session scratchpad)](docs/decision_log.md). Acceptance: [FLOOR-COMMONMODE-01 acceptance](docs/process/state_kernel.json). Note: Minted 2026-07-25. Quantified same day on a5 decode ABBA (10 complete blocks): implemented worst-case-sum half-width gives a 6.46 J comparative floor; a common-mode proxy gives 2.13 J, a 3x improvement — material, but still above that cell's 0.60 J point floor, so it does not by itself restore extraction under the current gate. Value is in tightening the labelled floor, not in avoiding the label. Fiducial share of the composed bound measured at 80-87%. |
| A48 | PHASE-SHARE-ESTIMAND-01 | P2 Next Slice | READY | Investigate the anti-correlated prefill/decode boundary error: energy a shift removes from one phase it adds to the other, so the phase-share estimand has ONE boundary nuisance parameter whose joint envelope is a curve, not a box. | Treating each phase's anchor envelope as an independent box double-spends the shared interior boundary and inflates uncertainty on exactly the split/share quantity the Splitwise replication needs. Evidence: Determined whether _corner_composed_anchor_shift_envelope treats the shared interior boundary independently; Joint envelope over the single boundary-position parameter derived by re-integration sweep (measured-curve arithmetic only); Quantified effect on the phase-asymmetry claim envelope versus the independent-box treatment. Authority: [2026-07-25 attribution-limit adjudication (Fable ruling + Sol replay; plan in session scratchpad)](docs/decision_log.md). Acceptance: [PHASE-SHARE-ESTIMAND-01 acceptance](docs/process/state_kernel.json). Note: Minted 2026-07-25 from the attribution-limit adjudication. Potentially the largest single win available for Splitwise sizing, at no instrument cost. |
| A49 | MODULARITY-01 | P3 Hardening Candidates | READY | Close the campaign-authoring modularity gap surveyed 2026-07-29: parameterize the campaign generator over a campaign-spec artifact and replace code-side literal assertions (analysis-manifest condition pairs, calibration scopes, phase-metric list) with registry-declared hash-validated sets. | Close the campaign-authoring modularity gap: campaign-spec-driven generation and registry-declared closed sets make every experiment axis swappable by config, per Ed's modularity directive. Evidence: Campaign generator is a parameterized function over a campaign-spec artifact (model, N, size profiles, block pattern, suite ref, run-ID prefix); a model swap touches one spec file and MODEL_TAG/PLAN_ID/run-ID prefixes derive from it with no parallel literal edits; Analysis-side closed sets (condition pairs, calibration scopes, phase-metric list) are declared in hash-bound registry artifacts and validated against those declarations, replacing the code-side literals at analysis_manifest.py:29-30,542-549 and detection_floor.py:87,89-95; Recorded-but-deferred residue dispositioned or re-queued: powermetrics references outside the adapter boundary, external-dataset ingestion, chat-template/thinking-mode seam, ABBA arity welded into three sites. Authority: [2026-07-29 modularity survey (Ed directive + per-axis grades)](docs/run_reports/2026-07-29-modularity-survey.md). Acceptance: [MODULARITY-01 acceptance](docs/process/state_kernel.json). Fence: Modularity applies to the harness, never to frozen claim pins: ratified hard literals (six-decimal pre-registration floor pins, lead-verified digests) stay anti-modular on purpose and must not be parameterized. (D-078 provenance amendment + D-079 operative-floor pins (hard literals are lead-verified, never parameterized)). Note: Minted 2026-07-29 from Ed's modularity directive. Survey verdict: runtime/telemetry Protocol layer and content-addressed provenance spine are already modular; the gap is campaign authoring above the adapter and literal assertions below the reader. Practical payoff lands with the planned Qwen3 cross-generation follow-up. |
| A50 | NVIDIA-PORTABILITY-01 | P3 Research Expansion | BLOCKED — ED-NVIDIA-RATIFY (Ed ratifies the staged plan and answers the intent question (claim vs appendix vs asset)) | NVIDIA extension, staged: S1 NVML counter-mechanics appendix + zero-claim capability probe (desk); S2 single-node RTX 3080 Ti instrument-portability study under four hard gates AFTER the Mac claims table closes; S3 split study deferred to the Phase-3 second paper. P1-008's acceptance-bar answers are the reopening trigger. | Staged NVIDIA extension: desk-only appendix + capability probe now; the single-node RTX instrument-portability study only after the Mac claims table is green and Ed ratifies; split study explicitly deferred to the Phase-3 second paper. Evidence: S1 landed: NVML counter-mechanics appendix drafted (desk-only) + zero-claim rig capability probe recorded + borrow-window doc staleness fixed; S2 (post-Mac-table, Ed-ratified): the four Sol gates — live promotion + retention closure; counter mechanics + rate-aware pulse anchor; RTX-specific floors with the minimal battery; one bounded named-GPU-board-boundary result (wall cross-check only if the D-092 meter passes its own battery); A calibrated non-result at any gate is recorded as publishable evidence and stops escalation (no ad hoc smoothing). Authority: [2026-08-02 two-lens extension consult (Sol feasibility + Fable science advisory), magistrate synthesis in .desk/nvidia-extension/SYNTHESIS.md — ED RATIFIES the S2 gate](docs/run_reports/2026-08-01-desk-adjudication-session.md). Acceptance: [NVIDIA-PORTABILITY-01 acceptance](docs/process/state_kernel.json). Fence: No NVIDIA energy number enters the December paper's claims table; S2 never binds the submission; mixed-boundary sums are never presented as split totals (Consult synthesis: December claims table stays Mac-only (both lenses)). |
| A51 | NODE-CUSTODY-DEFAULT-01 | P3 Hardening Candidates | READY | Decide and implement whether the production DEFAULT_RETENTION_ROOT should be process/instance-unique: it currently is a fixed shared temp path (a latent collision hazard for genuinely concurrent clients), but making it unique conflicts with next-session custody reclamation. Resolve the tradeoff or record it as accepted. | Harden the production DEFAULT_RETENTION_ROOT against concurrent-client collision while preserving next-session custody reclamation (the NEEDS_RULING tradeoff deferred from NVIDIA-RETENTION-FLAKE-01). Evidence: The production DEFAULT_RETENTION_ROOT no longer collides for genuinely concurrent NodeClients sharing a scope, without breaking next-session custody reclamation (a later process must still locate the manifest it is entitled to reclaim); A regression proves two default-constructed clients in one process do not clobber each other AND that the documented reclamation contract still resolves the correct manifest across process boundaries; No retention/custody assertion is weakened; only root selection changes. Authority: [NVIDIA-RETENTION-FLAKE-01 fix report F1/F3 (PR #97): unique default roots close concurrent collision but conflict with next-session reclamation](docs/run_reports/2026-08-03-desk-session.md). Acceptance: [NODE-CUSTODY-DEFAULT-01 acceptance](docs/process/state_kernel.json). Fence: Isolation-only: do not weaken any retention/custody assertion; the reclamation contract's cross-process manifest resolution must survive any default-root change (NVIDIA-RETENTION-FLAKE-01 test-side fix (PR #97) already closed the flake). Note: Deferred 2026-08-03 from NVIDIA-RETENTION-FLAKE-01 (PR #97 closed the test-side flake); the production hardening is a NEEDS_RULING tradeoff, non-blocking (no current concurrent-client scenario). |
| A52 | D080-TRIGGER-01 | P3 Hardening Candidates | BLOCKED — D-080-amendment (Ed ratifies the trigger cadence and the runner (cron routine vs manual)) | Wire D-080's standing fresh-eyes sweep to a REAL trigger (calendar cron or every-N-merged-PRs), run as a separate concurrent read-only instance per the Ed-validated 2026-08-03 pattern, findings delivered mid-flight; reconcile D-080 clause 4(ii)'s stale zero-unique-catch citation. | The fresh-eyes sweep fires without anyone remembering it, on a ratified cadence, as a concurrent read-only instance. Evidence: A ratified trigger exists (cron routine or PR-count hook) and has fired at least once; D-080 clause 4(ii)'s stale citation is reconciled by amendment. Authority: [D-080 + the 2026-08-03 sweep finding (never fired) + Ed's concurrent-audit validation](docs/decision_log.md). Acceptance: [D080-TRIGGER-01 acceptance](docs/process/state_kernel.json). Note: 2026-08-03: minted from the two-week soundness sweep's finding that D-080 has never fired, plus Ed's validated concurrent-audit pattern (memory: concurrent-fable-audit-pattern). Non-blocking hardening. |
| A53 | CGV-HARDEN-01 | P3 Hardening Candidates | READY | Harden runner-owned receipt persistence after validator --receipt-out removal: use a dirfd-relative receipt write that closes receipt-write TOCTOU and supplies fsync plus directory-sync atomicity. | The convening runner durably persists validator receipts through a dirfd-relative, crash-atomic, fsync-complete write path. Evidence: The convening runner persists the validator receipt with a dirfd-relative write that closes the receipt-write TOCTOU; Receipt publication is atomic and includes file fsync plus parent-directory sync; Regression tests distinguish path replacement, durability failure, and successful atomic publication. Authority: [2026-08-05 COLDGATE-VALIDATOR F3 consult Q2 receipt-persistence disposition](docs/process_traces/2026-08-05-cgv-f3-consult/SYNTHESIS.md). Acceptance: [CGV-HARDEN-01 acceptance](docs/process/state_kernel.json). Fence: Keep this row a sibling of COLDGATE-HANDOFF-01 and never merge them: durable receipt storage and validated-byte judge handoff have different contracts, tests, and failure consequences (2026-08-05 F3 consult Q2 dissent). Note: 2026-08-05: runner-scoped because PR #103 removed the validator's --receipt-out; deliberately registered as a sibling of, never folded into, COLDGATE-HANDOFF-01. |

### Shelved task records
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

# Agent Implementation Plan

This repository implements JouleWise, an extensible energy-characterization
benchmark for LLM inference across heterogeneous local hardware. The name is a
nod to JouleSort and Splitwise: energy measurement as the spine, split inference
as the first research application that validates the harness.

## Ground Rules For Agents

- At the start of every substantial run, read `RUN_STATE.md` first.
- For any new/random user task, triage it in `TASK_QUEUE.md` before deciding
  whether it outranks the current phase work.
- At the start of each phase or major step, apply
  `docs/planning_reflection_protocol.md` before implementation.
- At the end of every substantial run, update `RUN_STATE.md` and add or update a
  detailed report in `docs/run_reports/`. If advisor-visible state changed (a
  phase or gate closed, a verdict landed, the schedule moved), refresh
  `PROJECT_STATUS.md` too.
- Check `docs/decision_log.md` before re-deciding anything; record new design
  decisions there with options and considerations.
- Per-item phase status is asserted only in
  `docs/phase_N/phase_N_exit_checklist.md` (D-023); this file's checkboxes
  are a coarse mirror updated at slice/phase closes.
- Review `docs/risk_register.md` at phase starts and when a trigger fires.
- Keep run artifacts self-contained and reproducible.
- Prefer small vertical slices that produce complete run bundles.
- Treat unsupported hardware/model combinations as structured outcomes, not
  crashes.
- Keep runtime adapters separate from telemetry adapters.
- Make every result traceable to a config, raw power trace, event log, and
  reducer output.

## Single Source Of Truth Map

Detail lives in exactly one place; everything else links to it. When
documents disagree, fix the drift in the same run and note it in the run
report.

| Artifact | Owns |
|---|---|
| `AGENT_PLAN.md` (this file) | phase index, coarse status mirror, acceptance criteria (per-item status authority: the exit checklists, D-023) |
| `PROJECT_STATUS.md` | advisor-facing status/plan/architecture summary (derived; update when advisor-visible state changes) |
| `docs/phase_N/phase_N_plan.md` | step/slice detail: objectives, design, actions, evidence, fallbacks |
| `docs/phase_N/phase_N_exit_checklist.md` | evidence gates for closing phase N, and per-item status (the authority, D-023) |
| `TASK_QUEUE.md` | what to do next, and why it outranks the rest |
| `docs/agent_playbook.md` | per-mission execution guides for agents: read-first lists, code-level routes, verification, handoff checklists |
| `RUN_STATE.md` | current handoff: state, verification, next step |
| `docs/decision_log.md` | design decisions, options, considerations |
| `docs/risk_register.md` | risks, triggers, mitigations, descope ladder |
| `docs/milestones.md` | calendar constraints and phase target dates |
| `docs/contracts/measurement_methodology.md` | measurement rules (boundaries, clocks, statistics) |
| `docs/contracts/run_bundle_layout.md` | bundle artifact contract |
| `docs/contracts/adapter_contracts.md` | adapter behavior contracts |
| `docs/contracts/node_worker_protocol.md` | remote-execution protocol (transport-independent; pinned during 2K, reused by 2L + Phase 3) |

Superseded (2026-07-15, WO-021; D-043): `docs/process/state_kernel.json` is the sole editable authority for live work selection, while generated `TASK_QUEUE.md` and `RUN_STATE.md` regions are projections; see `docs/specs/c027/doc-008_state_kernel.md` §§3.1, 3.6, and 4.

## Canonical Architecture

```text
typed config
  -> controller
    -> transport adapter: local or ssh
    -> runtime adapter: mlx, vllm, llama.cpp (hailo: unsupported_workload — feasibility finding only)
    -> telemetry adapter: powermetrics, nvidia-smi, jetson rails, wall meter
  -> run bundle
    -> reducers
    -> dashboard / notebooks / report figures
```

## Phase Index

### Phase 1: Approval, Feasibility, And Measurement Design

Status: in progress (most design/feasibility items closed; the remaining
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


exec
/bin/zsh -lc "git status --short --branch; sed -n '1,174p' docs/council_log.md" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
## main...origin/main
# Council Log

Chronicle of multi-model review councils: sessions where more than one
model reviews, counterreviews, or votes on JouleWise work before it
lands. Companion to `docs/decision_log.md` (which records WHAT was
decided about the system; this file records HOW cross-model review
reached it). One entry per council session; keep entries concise —
positions, votes, resolutions, and follow-ups, not transcripts.

Cross-session model-allocation evidence — which instrument (gpt-5.6-sol,
Opus 5, Fable, or the lead at the bench) should be assigned to which task
class, and what each layer has actually caught — lives in
`docs/process/model_allocation_ledger.md`. This file remains the ONE home
for per-session deliberation narrative; that ledger is the ONE home for
the structured, adjudicable allocation record.

Standing council roles (adopted C-001; process decision D-031):

- **Claude (lead/orchestrator)** — scopes work, diagnoses live/hardware
  failures, runs adversarial review workflows, owns bookkeeping and the
  final merge decision, and is the only member that touches real
  hardware.
- **Codex / gpt-5.5 (peer implementer-reviewer)** — implements against
  pinned specs, counterreviews findings on its own code, reverse-reviews
  Claude's commits and orchestration decisions, and is asked for design
  judgment explicitly ("argue the tradeoffs before you code").
- **Opus subagents (fast reviewers)** — parallel lower-level sweeps
  (commit hygiene, docs consistency, fixture audits) whose findings feed
  the discussion; cheap enough to run every session.

(Amended 2026-07-08: the Opus fast-reviewer tier was dropped at C-006
after zero unique catches; lead-driven pipelines are the default per
C-010; Ed granted standing self-merge-with-review authority in the C-010
addendum.)

Disagreements are discussed in at most one or two rounds; unresolved
disagreements are decided by the lead and recorded here with the
dissent. Anything user-facing (push/merge/publish) follows the user's
standing instructions.

## Index

| ID | Date | Topic | Outcome |
|---|---|---|---|
| C-001 | 2026-07-06 | Adopt review/counterreview between Claude and Codex (2H precedent) | adopted; all 10 findings accepted, Codex improved the blocker fix design |
| C-002 | 2026-07-07 | Reverse review of the 9-commit vertical-slice series; push vs PR | PR convention adopted; run_id renamed; P2-008 promoted; D-023 extended; sweep step added |
| C-003 | 2026-07-07 | Research agenda: what else can the instrument answer; robustness; scale-up | Q4-Q6 promoted; detection floor = methodology centerpiece; D-014 uncertainty found unimplemented; nodes/<node_id> flagged as pre-multi-node breaking fix |
| C-004 | 2026-07-07 | Difficulty-graded scored workload suites; collect-more-per-run | affine_mod_ladder_v1 adopted as ONE quarantined profile; rich-telemetry parsing (P2-009) prioritized ahead of it; examiner reframe adopted |
| C-005 | 2026-07-07 | Steelmanned research agenda + workload expansion | 31 tiered questions + kill list; jw_mixed_v1 starter suite specified (→ P2-012) |
| C-006 | 2026-07-07 | Session trace + orchestration meta-review of the six-stream parallel day | 13 attributed catches; integration-review step vindicated; skills deduplicated; operation-loop installed |
| C-007 | 2026-07-07 | Whole-project design/planning council (user-directed) + P2-013 fix design | P2-013 re-ranked above 2M with raw-to-trace gate added in-stream; two-claim-track framing adopted; detection floor gets an owning Phase 4 gate; machine-state queue lanes; pre-2M contract amendments (P2-014) |
| C-008 | 2026-07-07 | Multi-stream hardware-prep session (4 streams, Opus directors + Codex volume), user-checkpointed mid-flight | 3.0.1 verdict replay_supported; P2-013 groups 1-4 (19/31 pins); 2K protocol v1 provisional; DOC-007 done; Slice 2O landed; ledgers v2 + calibration + wake-gap lessons folded into skills same-session |
| C-009 | 2026-07-07 | META-REVIEW of the orchestration system itself (user-directed): 2 blind Codex analyses vs Fable's blind positions → conferral → SIGNED consensus | Hybrid topology + lead stream-state table; foreground-wait orchestrators + STALLED-handback; heartbeat demoted to backstop; Codex up-stack (design freedom, schema drafts, lead-decision packets); docs single-writer end-state (run report = session record; council log = deliberation only; RUN_STATE = pointer; ledgers retire at integration WITH branch/hash pointer); retired-artifact pointer rule; codex-run patch queued; preflight gates (device inventory, quiet lock, provisional labels) |
| C-010 | 2026-07-08 | Resume+merge session — first full run under the C-009 topology (pointer entry; full record in the resume-merge run report) | Lead-driven pipelines validated (zero stalls, no subagent directors); B-14/B-15 wire pins overturned by lens review pre-hardware; fabricated-evidence defect caught at lead diff gate (B-44); Ed grants standing self-merge-with-review authority; final-head review rule adopted; PRs #8/#9/#10/#11 merged |
| C-011 | 2026-07-08 | Counter-review of the independent project critique (4 verification lenses + 5.5-high adjudication; full entry below) | Critique findings adjudicated into mechanics: fail-closed campaign runner, counterbalanced order manifest, reducer honesty flags, claims ladder (D-037), P2-015 ranked before 2M; merged as PR #12 |
| C-012 | 2026-07-08 | Site observatory stream (pointer entry; full record in run report `2026-07-08-site-observatory.md`) — dual-prior design round, 2 image-critique rounds, visual sign-off, counterreview, final-head gate | Data-driven status frontend merged as PR #13; fail-closed parser honesty enforced (2 counterreview blockers fixed); P2-017 per-source stamps closed; image-heavy analysis routed to Codex as standing doctrine (Ed) |
| C-013 | 2026-07-08 | Lakebed deployment stream (pointer entry; full record in run report `2026-07-08-lakebed-deploy.md`) — 5.5 impl + 6 platform-constraint fix rounds + fresh counterreview | Site live as a shareable capsule with a live GitHub freshness layer (fails soft); lead owns deploy/claim (no sandbox network); site regen+redeploy folded into the RUN_STATE end-of-work loop |
| C-014 | 2026-07-08 | Workload-suite science hardening (full entry below) — lead audit + scout + 3 design lenses + invited peer counterreview | Q4-at-L3 gap closed via `q4_l3_shape_grid_v1` (4x3 + holdouts); P2-015 expanded to comparative MDE floors; jw_mixed common-shape stratum (C-W.1 was unfalsifiable); P2-010 split substrate/smoke, scored ladder deferred; two-quiet-window plan; analysis-plans contract (D-038); program restructure (D-039); two lead designs overturned by invited peer |
| C-015 | 2026-07-08 | Benchmark expansion council (full entry below) — reach lenses R1/R2 + design lenses E1/E2 + peer counterreview | Suite architecture v2 (D-040: B×k bundles, one generic mechanism, per-item status model); interop direction (D-041: HumanEval-first imports, marker-shim energy layer, kill list); capability map landed in bank; R2 collect-now set spawned the window-a-capture stream; capstone stop-line + D-034 gate restated |
| C-016 | 2026-07-08 | Post-large-workload meta-reassessment (pointer entry; records: D-043, `~/.claude/skills/skill-usage-log.md`, run report addendum) — 4 analysts (council/decision/skill mining + cold-start derivability) + completeness critic, Workflow-orchestrated | Supersession drift named as THE recurring unfolded failure mode (~70% of doc defects) → D-043 write-time + sweep-time discipline; operative merge-authority contradiction fixed; 5 skill divergences fixed; codex-delegation rewritten procedure-first; clean-machine derivability closed (scripts/codex-run committed + orchestration.md pointer map); §10 post-large-workload trigger now standing |
| C-020 | 2026-07-08 | STOP-AND-ANALYZE WHOLE PROJECT: technical + research merit debate (full entry below) — 69-agent Codex assessment workflow + 2 independent Fable position papers + recorded Fable-vs-Codex debate; owner-directed | Merit verdict recorded (docs/reviews/2026-07-08-technical-merit-review.md); D-048 model-first split program + D-049 transfer-boundary accounting promoted; question ranking adjudicated (Q4→Q1 coupled #1, Token-Shape Null sustained #2, Q6 elevated #3, affine ladder = validity instrument); crossover prior corrected by arithmetic; cheap-validity priority set (bundle publication + external re-reduction first); repo-verified gaps: bundles unpublished, no LICENSE, D-033 strict-validation legacy bypass |
| C-019 | 2026-07-08 | Post-suite-build meta-reassessment (full entry below) — 4 analyst lanes (5.5-direction study over 43 invocations; calibration longitudinal; project status/value ranking; closure) + completeness critic | Direction doctrine folded into codex-delegation skill (precedence/autonomy/FIX-N/production-gate clauses; model-version scoping rule pre-upgrade); D-013 prose back-annotated marker-bounded; shakedown gate added to P2-015; P2-025 adjacency + P1-008 elevation (incl. examiner acceptance-bar ask); pre-#21 corpus validity noted (dict-read-scale overhead, no re-reduction); watch items: integration-after-oversight, Opus A/B |
| C-018 | 2026-07-08 | D-013 alignment-capture window fix (parallel session; full entry below) | sampling_stopped stamped before alignment capture (PR #21: `255a7e6`, bookkeeping `c2e51b2`, merge `49c5b66`); suite 734; D-013 prose back-annotated to marker-bounded wording in the reassessment batch |
| C-017 | 2026-07-08 | Suite-build adjudication + implementation gates (full entry below) — Codex disposition draft + fresh adversarial round + lead calls; 11 unit lenses + 1 Opus outage substitute + 7-reviewer oversight + 3 final-head + integration | 37 amendments dispositioned → D-044..D-047; substrate/ladder/generators BUILT and merged (PRs #17/#18/#20/#19, suite 732); 3 lead live-only catches (refs, strict rollup, sampler namespace); oversight caught 2 validation holes pre-merge; PR #18 base-retarget slip recovered via #20 |
| C-021 | 2026-07-09 | Advisor status-site live-depth refresh (pointer entry; D-051; run report `2026-07-09-advisor-status-site.md`) | Static generated pages remain the audit fallback; Lakebed gets fail-soft live overlays from current GitHub markdown; Story page volatile counts removed; advisor cockpit expanded with attention, readiness, evidence, and claim-ceiling panels; gpt-5.5-high counterreview used before deploy |
| C-022 | 2026-07-09 | CP-5 resume session (pointer entry; run report `2026-07-09-cp5-resume.md` owns the full trace) — lead-driven, ~35 codex sessions: implementation, fix rounds, 12+ lenses/final-head passes, 2 integration reviews | PRs #22..#28 merged (merge-gate shape held: lens→fix→lead live gate→fresh final-head→CI→merge); final-head layer caught 3 blockers + 7 should-fixes post-lens; CI merge-ref caught the one cross-branch interaction (#23 fixtures × #27 strict rules) no other layer could see; 1 lead prompt-defect (inferred-sidecar pin) caught and refixed; methodology synthesis + suite_next packet adjudicated (CP-6); D-047 sampler clause amended (fail-closed); stop card CLEARED; Window-A GO |
| C-023 | 2026-07-09 | Scientific-rigor review of the measurement suite, benchmark, and full question bank (user-directed; full record `docs/reviews/2026-07-09-scientific-rigor-review.md`) — 4 fresh 5.5 lenses (metrology, benchmark/stats, per-question bank audit, advisor simulation) + independent lead read + 1 bidirectional discussion round | Verdict: strong provisional, advisor sign-off after a named all-software artifact list (error budget/P2-015 combined spec, analysis registry + multiplicity policy, canonical RQ registry + linter, frozen headline, contrast-level stats amendment, ordering executability, token-normalization contract); every blocker no-hardware-fixable; C5-1.1 blocker OVERTURNED in discussion (already contract-capped by C-014/D-037); ordering gap (C-015 promise vs manifest_order execution) elevated to pre-campaign; queue impact deferred to the step-2 planning session |
| C-024 | 2026-07-09 | Spec-fleshing wave 1 (pointer entry; run report `2026-07-09-spec-fleshing-wave1.md`) — 4 worktree streams (5.5 implement), 4 counterreview lenses, 3 fix rounds, 4 final-head + 1 tail-verification pass, integration review | PRs #29..#32 merged (D-052..D-055 ratified: scope contract, contrast-level stats + registry, false-effect guard floor, RQ registry); R2's estimator kill (percentile-UCB unidentifiable at n=10) was the session's decisive catch; integration review caught 5 cross-stream seam drifts (S1/S2 written against pre-S3 contract text); P2-015-PREP (queue rank 0) closed; checkpoint-push cadence adopted mid-session (Ed) |
| C-025 | 2026-07-09 | Wave 2 — ultracode workflow build (pointer entry; run report `2026-07-09-spec-fleshing-wave2.md`) — 46-agent workflow (4 impl streams, 8 lenses, severity-tiered refuters) + 2 lead-driven reinforcement streams + 6 final-heads + tail verification + combined-ref check + integration review | PRs #33..#38 merged (D-056..D-059 ratified: order policies + order_row, drift-is-a-bound + stable reason codes, token-normalization contract, claims-lint CI enforcement); refuter layer killed 10 findings pre-triage; final-heads caught 2 live-path defects (MLX position under rotation; linter false-negative regression); mutation testing debuted in the test-audit lens; combined-ref suite check validated the p2029 x p2030 strict-surface interaction pre-merge; suite 877 |
| C-026 | 2026-07-09 | P2-034 broad campaign packs (pointer entry; run report `2026-07-09-p2034-broad-packs.md`) — design-round-first (memo ratified w/ 3 pins), single worktree stream, dual lenses, final-head CLEAN | PR #39 merged; six packs, pack lint errors=0; compliance lens caught a char-level registry drift the linter cannot see (code-span nesting) + a scorer-leak + P2-022 structure flattening; executability lens caught the external-lab cold-start gap; pre-hardware campaign surface COMPLETE (every pre_hardware_preparable=fully row packed) |
| C-027 | 2026-07-09 | Whole-project council review with gpt-5.6-sol xhigh (first production session; 7 lenses: topdocs/rigor/stats/meta/reverse/arch/negspace + counterreview + independent Fable-tier final examiner; full record `docs/reviews/2026-07-09-c027-whole-project-review.md`) | 8 blocker clusters confirmed (token-denominator mislabel, superseded D-053 prose, RUN_STATE dual next-action, claim machinery unimplemented+unowned, empty D-050 manifest, four D-031 direct-to-main commits, evidence-integrity trio, protocol blockers); claim surfaces corrected same session; 14 follow-up queue rows + NV-GATE-2 additions to P2-005; D-060 proposed + D-061..D-063 accepted; counterreview reversed the lead twice (legacy-gate framing, restructure staging) |
| C-038 | 2026-07-25/26 | FLOOR-LABEL-01 gauntlet close (D-078 cl.11 labelled attribution-limited floors) + quiet-window collection; Ed re-proportioned the instrument mix mid-session (Opus 5 subagents = primary delegated lieutenant, Fable on genuine need, Sol = execution workhorse, lead adjudicates); full entry below | Opus-contract lens verdict COMPARATIVE COVERAGE: COMPLETE with 4 should-fix / 4 nits, incl. the `_combined_floor` key-sniffing misattribution mirrored bug-for-bug into `artifact.py` (so validation recomputes the same wrong answer and ships) and the ratio-unit floor/diagnostic inversion; Sol xhigh audit's 1 blocker (runnable V3 probe: comparative blocks minted WITHOUT admissible half-widths validate clean, floor_gate 5e-324 J vs 2.6484 J) ADJUDICATED DOWN to registered limitation L1 — first concrete demonstration of L1, and FLOOR-LABEL-01 recorded as modestly WIDENING its blast radius; Sol xhigh clock diagnosis root-caused window C to transient wall-vs-monotonic slew over the 5 ms ceiling (7.769 ms verified) and corrected the lead's duration hypothesis; Fable adjudication (zero tool uses, 108 s) OVERTURNED the lead's own self-diagnosis and named the disposition (rigorous on work products, exempts its own premises about the environment) → rules R1/R2/R3, no demotion; window B 59/59 clean (whole-window verdict PENDING), window C failed twice on clock slew, window D not started; FIVE lead errors recorded, incl. the ~10-hour lost quiet window (untracked `nohup` + turn ended with no wake source) and TWO exit-status masking incidents → generalization: EXIT STATUS IS NOT EVIDENCE OF WORK DONE |
| C-040 | 2026-08-01/02 | Commit-3 cooldown-join gauntlet: five fix rounds and three cold-gate dispositions | PR #93 merged after the custody micro-commit and exact-set pin; D-105 recorded the residual recognizer boundary; every review layer produced unique catches |
| C-041 | 2026-08-03 | D100-BII nested-closure arc and CAL-BRACKET design consult | Three closure formulations failed and the bench loop stopped for decision-level rulings; CAL-BRACKET F3 escalated; MINT-GENERALIZE tooling merged |
| C-042 | 2026-08-03 | Ed-requested pre-ruling debate: 2-round adversarial Sol xhigh consult over the D-108/D-109 decision packets (MCP discussion lane, read-only; Sol instructed to bench-verify packet claims; record .desk/2026-08-03-sol-debate-d108-d109.md); Ed then ruled by explicit deferral to the joint position | Both packets materially changed before ruling: Sol caught the overstated three-subject manual-verification claim and broke the original A-min formulation (writer crash-window; prefix-subset is not anti-rollback) — both lead-verified and adopted (reservation-first + repo-committed head pin now D-109 law); Sol's code refutation of the magistrate's two-subject license-surface counter adopted into D-108 clause 2; magistrate context (schedule slack, metrology pivot, shared-R2 marginal cost) flipped Sol's B recommendation to A-min-with-reservation, withdrawn on the record; residual dissents preserved in both decision texts |
| C-043 | 2026-07-22 | D-078 P0 instrument-repair close-out (round-8/8b landing + §C-028 delta re-audit with 3 lenses / 11 refuter runs, round-9 FINAL confirmation, L1 adjudication, PR #79) | Round-8b delta re-audit caught the understated-B_fiducial ClockStamp blocker two audited rounds missed; refuters killed 2 findings, narrowed 1, split 1 (lead-synthesized); CR9-1 adjudicated as registered limitation L1 + FLOOR-BIND-01; failure modes recorded (content-filter refuter kills -> data-quality rephrase; bench-edit-during-enforced-scope false attribution; review-genre null-final recovery) |
| C-044 | 2026-07-24 | NEG-8 drift-gate estimand debate (Ed-directed pre-ratification cross-model debate; Sol xhigh peer vs lead ruling) | Peer disagreed on inferential role (screen != stability proof) and was adjudicated CORRECT; Ed ratified the amended screen+budget design (option F full) with rigor-spiral + no-invented-physics guardrails; second recorded case of peer design judgment overturning a lead ruling pre-implementation |
| C-045 | 2026-07-24/25 | NEG-8 SCREEN+BUDGET audit gauntlet: four audit rounds and paired contract/execution refuters | PR #85 merged after three fix rounds; the paired lenses materially changed triage, and the residual custody-hardening work was queued |
| C-046 | 2026-07-26 | Retrospective: CAL-REBRACKET-01 max-bracket consumption gauntlet (PR #86) | Governed consumption-time authenticated re-derivation landed after three implementation rounds and three independent audits; a9/a10 replays passed with widened members and unchanged point estimates |
| C-047 | 2026-08-03 | The 16h runway (Ed-granted; joint Fable+Sol decision authority; concurrent sweep instance mid-flight): D-108/D-109 debate+rulings executed, D-110/D-111 sweep-triggered rulings, winB STOP cold gate -> D-112, two Sol gauntlets, pinned byte-identical mint replay, checkpoint for harness switch | D-108 closed via PR #99 + re-record; CAL-BRACKET held at 2e61ff9 (B1 residual, rule-11 gate owed); winB license exhausted as drawn (r06 disposition parked for Ed); mint chain D-110-blocked; CLAIMS_STATUS section 1 honestly NONE; sweep propagation fixes landed; layer yield in the run report |
| C-048 | 2026-08-04 | Integration-collision resolution on the CAL-BRACKET-D079-01 lead gate: bounded pre-decision Sol HIGH consult -> consult-shaped signature amendment -> fresh delta re-audit -> bench guard hardening -> merge-ref CI | The delta re-audit PROVED a live repr-'None' default spoof against the rendered-signature guard (hardened with a regression); the consult corrected the byte-identity oracle to integration-tree core-vs-wrapper parity (a historical-digest replay would have contradicted D-110); lead integration-tree replay 2487 OK exit-0 unpiped; PR #100 gate-complete, merged 2026-08-05 (`f75d12b`) |
| C-049 | 2026-08-05/06 | The 12h autonomous marathon: six PRs (#102-#104, #106-#108) + PR #109 issuance gauntlet; two rule-11 escalation consults (CGV F3 closure, QG census Option C); the D-079 issuance cold gate (split verdict, HOLD upheld); D-113/D-115/D-116; then the first re-mint consumption attempt exposed a structural closure -> Sol xhigh fork consult | The cold gate's HOLD prevented an irreversible ledger write paired with a production-refused artifact (F1 no-consumer-path, F2 digest-role coupling — issuance reframed as implementation and re-gauntleted as PRs #108/#109); xhigh delta re-audits again caught introduced defects (QG init-durability F1; CGV live-proved receipt-serialization B1 + phantom-fence B2); historical max-bracket consumption proved structurally closed at main — Option 2 (three fresh prospective windows) recommended by consult + magistrate; Ed's ruling OWED at close |

---

## C-001: Review/counterreview adopted (Slice 2H)

- Date: 2026-07-06. Participants: Claude (lead), Codex gpt-5.5 (author +
  counterreviewer), 22 review/verification subagents.
- Shape: Codex implemented 2H → Claude live-verified → a three-lens
  adversarial review workflow (contract / correctness / test-adequacy;
  every finding survived an independent refutation attempt) confirmed
  10 findings (1 blocker, 6 should-fix, 3 nits) and refuted 2 → Codex
  counterreviewed as a peer.
- Votes/positions: Codex accepted all 10 findings (refuted none) and,
  invited to argue design before coding, proposed a better blocker fix
  than either option the lead posed (`AdapterFailure` structured
  exception; controller maps the true `FailureReason`).
- Resolution: all fixes applied; suite 251 green; live re-verified
  (fail-fast at idle_baseline, `permission_denied`, no fabricated
  baseline). Precedent: green tests are necessary, never sufficient —
  the blocker was invisible to a fully green suite.
(Amended 2026-07-08: the Opus-refuter tier was dropped at C-006 after
zero unique catches; refutation-as-protocol lives on with fresh Codex
refuters, as recorded in the adversarial-review evolution.)

## C-002: Reverse review of the vertical-slice series; push vs PR

- Date: 2026-07-07. Participants: Claude (lead), Codex gpt-5.5 (reverse
  reviewer of Claude's commits AND decisions), 2 Opus subagents (commit
  hygiene; docs consistency).
- Subject: the 9 unpushed commits (`10a570d`..`123d87a`) and five of
  Claude's orchestration decisions (flagship config mutation, 20 Hz mock
  workaround, provisional D-016 wording, main-branch convention,
  bookkeeping fidelity).
- Findings that survived: (1) stale gate-state prose in 6 files
  (Opus sweep + Codex independently convergent) — README/playbook test
  counts, phase-1 sudoers rows, phase-2 status paragraph contradicting
  its own matrix, PROJECT_STATUS blocked-items, wrong skip count, stale
  CI run number; (2) Codex-unique: the flagship config kept run_id
  `example-mac-mlx-local` across a workload-semantics change — explicit
  run_ids bypass hash suffixing, blurring provenance; (3) both reviewers
  independently: the committed sudoers line exposed the OS username.
  Commit hygiene otherwise CLEAN (messages match diffs, test-count chain
  reconciles, fixture justified, no secrets); CI risk assessed low
  (Codex ran the suite, config validation, and mock e2e itself).
- Discussion round (positions → resolution):
  - D1 flagship mutability: Claude held configs are entrypoints (run
    identity = config hash, D-022/D-029) but conceded the run_id rename
    (`example-mac-mlx-local-512t`); Codex concurred and withdrew the
    separate-config ask ("a committed known-unmeasurable config is a
    footgun"); the short-window finding lives in the 2I run report.
  - D2 P2-008 urgency: consensus rank 3 with a hard "before 2K/2L
    bring-up" gate (mock telemetry under SystemClock is now real-runtime
    test infrastructure); not above 2M/Stage 3.0, which don't touch the
    edge.
  - D3 bookkeeping drift (structural): consensus two-part fix — D-023
    extension (prose status summaries carry an as-of date and defer to
    checklist matrix rows; no re-narrated gate lists) + a standing
    end-of-session docs-consistency sweep by a fast subagent
    (RUN_STATE end-of-work step 7). This session is the proof: the sweep
    caught everything the peer reviewer caught.
  - Push vs PR: Codex recommended branch+PR (one GitHub-readable diff +
    CI before main for a mixed code/config/docs series); Claude accepted;
    unanimous. Convention adopted for multi-commit sessions (D-031).
- Pre-PR blockers (all applied in the fix-up commit): staleness fixes,
  run_id rename + hash pin, `<local_user>` genericization of the sudoers
  line in docs, this log, queue re-rank.
- Dissents: none outstanding.
- Follow-up (user direction, same day): next multi-stream batch
  (2M / P2-008 / kv-size) runs as parallel worktree streams, each owned
  by a Fable orchestrator subagent driving its own Codex thread, landing
  as separate PRs (D-031 execution-topology addendum).

## C-003: Research agenda expansion (ideation council)

- Date: 2026-07-07. Participants: Claude (lead), Codex gpt-5.5 (ideation +
  critique), 3 Opus subagents (RQ-from-instrument; collection feasibility;
  robustness + scale-up).
- Key outputs: Codex's fixed-vs-marginal energy model (adopted as Q4;
  subsumes prefill exponent) and compositional split prediction (folded
  into Q1's method); ranking stability (Q5); boundary sensitivity (Q6).
  Opus ground truth: detection floor (idle stddev 5.4 W > mean 3.5 W),
  ~30-75 bundles/hour throughput with automation (not schema) as the
  campaign blocker, `SummaryMetrics.uncertainty` is a documented-but-DEAD
  field (D-014 never implemented), and the composite bundle layout
  hardcodes `nodes/prefill|decode` — a breaking generalization
  (`nodes/<node_id>`) required BEFORE any multi-node data.
- Dissent adjudicated: Codex voted to cut "variance" as an RQ
  (methodology, not science); lead partially conceded — it became the
  methodology centerpiece (detection floor) rather than a numbered RQ.
- Resolutions: promote Q4-Q6; queue D-014 implementation as the highest
  credibility-per-hour item; question bank doc created.


codex
The log spans several instrumentation eras: early councils report findings narratively, while later gauntlets explicitly label “unique catches.” I’m normalizing only defect catches that the entry attributes to one of the requested layers; design contributions, duplicates, clean confirmations, refutations/suppressions, and findings merely repeated by another layer will not inflate the totals. Severity will remain “unstated” unless the entry itself assigns one.
exec
/bin/zsh -lc "rg -n -i -C 3 'unique catch|layer catch|per-layer|pre-decision|predecision|implementation.audit|implementation audit|delta re.audit|cold gate|cold-gate|refuter|lead bench|lead live|lead diff|\\bCI\\b|integration review|oversight|prune lens|spend|lead error|piped|exit.status|RUN_STATE|index row' docs/council_log.md" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
29-  the discussion; cheap enough to run every session.
30-
31-(Amended 2026-07-08: the Opus fast-reviewer tier was dropped at C-006
32:after zero unique catches; lead-driven pipelines are the default per
33-C-010; Ed granted standing self-merge-with-review authority in the C-010
34-addendum.)
35-
--
50-| C-006 | 2026-07-07 | Session trace + orchestration meta-review of the six-stream parallel day | 13 attributed catches; integration-review step vindicated; skills deduplicated; operation-loop installed |
51-| C-007 | 2026-07-07 | Whole-project design/planning council (user-directed) + P2-013 fix design | P2-013 re-ranked above 2M with raw-to-trace gate added in-stream; two-claim-track framing adopted; detection floor gets an owning Phase 4 gate; machine-state queue lanes; pre-2M contract amendments (P2-014) |
52-| C-008 | 2026-07-07 | Multi-stream hardware-prep session (4 streams, Opus directors + Codex volume), user-checkpointed mid-flight | 3.0.1 verdict replay_supported; P2-013 groups 1-4 (19/31 pins); 2K protocol v1 provisional; DOC-007 done; Slice 2O landed; ledgers v2 + calibration + wake-gap lessons folded into skills same-session |
53:| C-009 | 2026-07-07 | META-REVIEW of the orchestration system itself (user-directed): 2 blind Codex analyses vs Fable's blind positions → conferral → SIGNED consensus | Hybrid topology + lead stream-state table; foreground-wait orchestrators + STALLED-handback; heartbeat demoted to backstop; Codex up-stack (design freedom, schema drafts, lead-decision packets); docs single-writer end-state (run report = session record; council log = deliberation only; RUN_STATE = pointer; ledgers retire at integration WITH branch/hash pointer); retired-artifact pointer rule; codex-run patch queued; preflight gates (device inventory, quiet lock, provisional labels) |
54:| C-010 | 2026-07-08 | Resume+merge session — first full run under the C-009 topology (pointer entry; full record in the resume-merge run report) | Lead-driven pipelines validated (zero stalls, no subagent directors); B-14/B-15 wire pins overturned by lens review pre-hardware; fabricated-evidence defect caught at lead diff gate (B-44); Ed grants standing self-merge-with-review authority; final-head review rule adopted; PRs #8/#9/#10/#11 merged |
55-| C-011 | 2026-07-08 | Counter-review of the independent project critique (4 verification lenses + 5.5-high adjudication; full entry below) | Critique findings adjudicated into mechanics: fail-closed campaign runner, counterbalanced order manifest, reducer honesty flags, claims ladder (D-037), P2-015 ranked before 2M; merged as PR #12 |
56-| C-012 | 2026-07-08 | Site observatory stream (pointer entry; full record in run report `2026-07-08-site-observatory.md`) — dual-prior design round, 2 image-critique rounds, visual sign-off, counterreview, final-head gate | Data-driven status frontend merged as PR #13; fail-closed parser honesty enforced (2 counterreview blockers fixed); P2-017 per-source stamps closed; image-heavy analysis routed to Codex as standing doctrine (Ed) |
57:| C-013 | 2026-07-08 | Lakebed deployment stream (pointer entry; full record in run report `2026-07-08-lakebed-deploy.md`) — 5.5 impl + 6 platform-constraint fix rounds + fresh counterreview | Site live as a shareable capsule with a live GitHub freshness layer (fails soft); lead owns deploy/claim (no sandbox network); site regen+redeploy folded into the RUN_STATE end-of-work loop |
58-| C-014 | 2026-07-08 | Workload-suite science hardening (full entry below) — lead audit + scout + 3 design lenses + invited peer counterreview | Q4-at-L3 gap closed via `q4_l3_shape_grid_v1` (4x3 + holdouts); P2-015 expanded to comparative MDE floors; jw_mixed common-shape stratum (C-W.1 was unfalsifiable); P2-010 split substrate/smoke, scored ladder deferred; two-quiet-window plan; analysis-plans contract (D-038); program restructure (D-039); two lead designs overturned by invited peer |
59-| C-015 | 2026-07-08 | Benchmark expansion council (full entry below) — reach lenses R1/R2 + design lenses E1/E2 + peer counterreview | Suite architecture v2 (D-040: B×k bundles, one generic mechanism, per-item status model); interop direction (D-041: HumanEval-first imports, marker-shim energy layer, kill list); capability map landed in bank; R2 collect-now set spawned the window-a-capture stream; capstone stop-line + D-034 gate restated |
60-| C-016 | 2026-07-08 | Post-large-workload meta-reassessment (pointer entry; records: D-043, `~/.claude/skills/skill-usage-log.md`, run report addendum) — 4 analysts (council/decision/skill mining + cold-start derivability) + completeness critic, Workflow-orchestrated | Supersession drift named as THE recurring unfolded failure mode (~70% of doc defects) → D-043 write-time + sweep-time discipline; operative merge-authority contradiction fixed; 5 skill divergences fixed; codex-delegation rewritten procedure-first; clean-machine derivability closed (scripts/codex-run committed + orchestration.md pointer map); §10 post-large-workload trigger now standing |
61-| C-020 | 2026-07-08 | STOP-AND-ANALYZE WHOLE PROJECT: technical + research merit debate (full entry below) — 69-agent Codex assessment workflow + 2 independent Fable position papers + recorded Fable-vs-Codex debate; owner-directed | Merit verdict recorded (docs/reviews/2026-07-08-technical-merit-review.md); D-048 model-first split program + D-049 transfer-boundary accounting promoted; question ranking adjudicated (Q4→Q1 coupled #1, Token-Shape Null sustained #2, Q6 elevated #3, affine ladder = validity instrument); crossover prior corrected by arithmetic; cheap-validity priority set (bundle publication + external re-reduction first); repo-verified gaps: bundles unpublished, no LICENSE, D-033 strict-validation legacy bypass |
62:| C-019 | 2026-07-08 | Post-suite-build meta-reassessment (full entry below) — 4 analyst lanes (5.5-direction study over 43 invocations; calibration longitudinal; project status/value ranking; closure) + completeness critic | Direction doctrine folded into codex-delegation skill (precedence/autonomy/FIX-N/production-gate clauses; model-version scoping rule pre-upgrade); D-013 prose back-annotated marker-bounded; shakedown gate added to P2-015; P2-025 adjacency + P1-008 elevation (incl. examiner acceptance-bar ask); pre-#21 corpus validity noted (dict-read-scale overhead, no re-reduction); watch items: integration-after-oversight, Opus A/B |
63-| C-018 | 2026-07-08 | D-013 alignment-capture window fix (parallel session; full entry below) | sampling_stopped stamped before alignment capture (PR #21: `255a7e6`, bookkeeping `c2e51b2`, merge `49c5b66`); suite 734; D-013 prose back-annotated to marker-bounded wording in the reassessment batch |
64:| C-017 | 2026-07-08 | Suite-build adjudication + implementation gates (full entry below) — Codex disposition draft + fresh adversarial round + lead calls; 11 unit lenses + 1 Opus outage substitute + 7-reviewer oversight + 3 final-head + integration | 37 amendments dispositioned → D-044..D-047; substrate/ladder/generators BUILT and merged (PRs #17/#18/#20/#19, suite 732); 3 lead live-only catches (refs, strict rollup, sampler namespace); oversight caught 2 validation holes pre-merge; PR #18 base-retarget slip recovered via #20 |
65-| C-021 | 2026-07-09 | Advisor status-site live-depth refresh (pointer entry; D-051; run report `2026-07-09-advisor-status-site.md`) | Static generated pages remain the audit fallback; Lakebed gets fail-soft live overlays from current GitHub markdown; Story page volatile counts removed; advisor cockpit expanded with attention, readiness, evidence, and claim-ceiling panels; gpt-5.5-high counterreview used before deploy |
66:| C-022 | 2026-07-09 | CP-5 resume session (pointer entry; run report `2026-07-09-cp5-resume.md` owns the full trace) — lead-driven, ~35 codex sessions: implementation, fix rounds, 12+ lenses/final-head passes, 2 integration reviews | PRs #22..#28 merged (merge-gate shape held: lens→fix→lead live gate→fresh final-head→CI→merge); final-head layer caught 3 blockers + 7 should-fixes post-lens; CI merge-ref caught the one cross-branch interaction (#23 fixtures × #27 strict rules) no other layer could see; 1 lead prompt-defect (inferred-sidecar pin) caught and refixed; methodology synthesis + suite_next packet adjudicated (CP-6); D-047 sampler clause amended (fail-closed); stop card CLEARED; Window-A GO |
67-| C-023 | 2026-07-09 | Scientific-rigor review of the measurement suite, benchmark, and full question bank (user-directed; full record `docs/reviews/2026-07-09-scientific-rigor-review.md`) — 4 fresh 5.5 lenses (metrology, benchmark/stats, per-question bank audit, advisor simulation) + independent lead read + 1 bidirectional discussion round | Verdict: strong provisional, advisor sign-off after a named all-software artifact list (error budget/P2-015 combined spec, analysis registry + multiplicity policy, canonical RQ registry + linter, frozen headline, contrast-level stats amendment, ordering executability, token-normalization contract); every blocker no-hardware-fixable; C5-1.1 blocker OVERTURNED in discussion (already contract-capped by C-014/D-037); ordering gap (C-015 promise vs manifest_order execution) elevated to pre-campaign; queue impact deferred to the step-2 planning session |
68:| C-024 | 2026-07-09 | Spec-fleshing wave 1 (pointer entry; run report `2026-07-09-spec-fleshing-wave1.md`) — 4 worktree streams (5.5 implement), 4 counterreview lenses, 3 fix rounds, 4 final-head + 1 tail-verification pass, integration review | PRs #29..#32 merged (D-052..D-055 ratified: scope contract, contrast-level stats + registry, false-effect guard floor, RQ registry); R2's estimator kill (percentile-UCB unidentifiable at n=10) was the session's decisive catch; integration review caught 5 cross-stream seam drifts (S1/S2 written against pre-S3 contract text); P2-015-PREP (queue rank 0) closed; checkpoint-push cadence adopted mid-session (Ed) |
69:| C-025 | 2026-07-09 | Wave 2 — ultracode workflow build (pointer entry; run report `2026-07-09-spec-fleshing-wave2.md`) — 46-agent workflow (4 impl streams, 8 lenses, severity-tiered refuters) + 2 lead-driven reinforcement streams + 6 final-heads + tail verification + combined-ref check + integration review | PRs #33..#38 merged (D-056..D-059 ratified: order policies + order_row, drift-is-a-bound + stable reason codes, token-normalization contract, claims-lint CI enforcement); refuter layer killed 10 findings pre-triage; final-heads caught 2 live-path defects (MLX position under rotation; linter false-negative regression); mutation testing debuted in the test-audit lens; combined-ref suite check validated the p2029 x p2030 strict-surface interaction pre-merge; suite 877 |
70-| C-026 | 2026-07-09 | P2-034 broad campaign packs (pointer entry; run report `2026-07-09-p2034-broad-packs.md`) — design-round-first (memo ratified w/ 3 pins), single worktree stream, dual lenses, final-head CLEAN | PR #39 merged; six packs, pack lint errors=0; compliance lens caught a char-level registry drift the linter cannot see (code-span nesting) + a scorer-leak + P2-022 structure flattening; executability lens caught the external-lab cold-start gap; pre-hardware campaign surface COMPLETE (every pre_hardware_preparable=fully row packed) |
71:| C-027 | 2026-07-09 | Whole-project council review with gpt-5.6-sol xhigh (first production session; 7 lenses: topdocs/rigor/stats/meta/reverse/arch/negspace + counterreview + independent Fable-tier final examiner; full record `docs/reviews/2026-07-09-c027-whole-project-review.md`) | 8 blocker clusters confirmed (token-denominator mislabel, superseded D-053 prose, RUN_STATE dual next-action, claim machinery unimplemented+unowned, empty D-050 manifest, four D-031 direct-to-main commits, evidence-integrity trio, protocol blockers); claim surfaces corrected same session; 14 follow-up queue rows + NV-GATE-2 additions to P2-005; D-060 proposed + D-061..D-063 accepted; counterreview reversed the lead twice (legacy-gate framing, restructure staging) |
72:| C-038 | 2026-07-25/26 | FLOOR-LABEL-01 gauntlet close (D-078 cl.11 labelled attribution-limited floors) + quiet-window collection; Ed re-proportioned the instrument mix mid-session (Opus 5 subagents = primary delegated lieutenant, Fable on genuine need, Sol = execution workhorse, lead adjudicates); full entry below | Opus-contract lens verdict COMPARATIVE COVERAGE: COMPLETE with 4 should-fix / 4 nits, incl. the `_combined_floor` key-sniffing misattribution mirrored bug-for-bug into `artifact.py` (so validation recomputes the same wrong answer and ships) and the ratio-unit floor/diagnostic inversion; Sol xhigh audit's 1 blocker (runnable V3 probe: comparative blocks minted WITHOUT admissible half-widths validate clean, floor_gate 5e-324 J vs 2.6484 J) ADJUDICATED DOWN to registered limitation L1 — first concrete demonstration of L1, and FLOOR-LABEL-01 recorded as modestly WIDENING its blast radius; Sol xhigh clock diagnosis root-caused window C to transient wall-vs-monotonic slew over the 5 ms ceiling (7.769 ms verified) and corrected the lead's duration hypothesis; Fable adjudication (zero tool uses, 108 s) OVERTURNED the lead's own self-diagnosis and named the disposition (rigorous on work products, exempts its own premises about the environment) → rules R1/R2/R3, no demotion; window B 59/59 clean (whole-window verdict PENDING), window C failed twice on clock slew, window D not started; FIVE lead errors recorded, incl. the ~10-hour lost quiet window (untracked `nohup` + turn ended with no wake source) and TWO exit-status masking incidents → generalization: EXIT STATUS IS NOT EVIDENCE OF WORK DONE |
73:| C-040 | 2026-08-01/02 | Commit-3 cooldown-join gauntlet: five fix rounds and three cold-gate dispositions | PR #93 merged after the custody micro-commit and exact-set pin; D-105 recorded the residual recognizer boundary; every review layer produced unique catches |
74-| C-041 | 2026-08-03 | D100-BII nested-closure arc and CAL-BRACKET design consult | Three closure formulations failed and the bench loop stopped for decision-level rulings; CAL-BRACKET F3 escalated; MINT-GENERALIZE tooling merged |
75-| C-042 | 2026-08-03 | Ed-requested pre-ruling debate: 2-round adversarial Sol xhigh consult over the D-108/D-109 decision packets (MCP discussion lane, read-only; Sol instructed to bench-verify packet claims; record .desk/2026-08-03-sol-debate-d108-d109.md); Ed then ruled by explicit deferral to the joint position | Both packets materially changed before ruling: Sol caught the overstated three-subject manual-verification claim and broke the original A-min formulation (writer crash-window; prefix-subset is not anti-rollback) — both lead-verified and adopted (reservation-first + repo-committed head pin now D-109 law); Sol's code refutation of the magistrate's two-subject license-surface counter adopted into D-108 clause 2; magistrate context (schedule slack, metrology pivot, shared-R2 marginal cost) flipped Sol's B recommendation to A-min-with-reservation, withdrawn on the record; residual dissents preserved in both decision texts |
76:| C-043 | 2026-07-22 | D-078 P0 instrument-repair close-out (round-8/8b landing + §C-028 delta re-audit with 3 lenses / 11 refuter runs, round-9 FINAL confirmation, L1 adjudication, PR #79) | Round-8b delta re-audit caught the understated-B_fiducial ClockStamp blocker two audited rounds missed; refuters killed 2 findings, narrowed 1, split 1 (lead-synthesized); CR9-1 adjudicated as registered limitation L1 + FLOOR-BIND-01; failure modes recorded (content-filter refuter kills -> data-quality rephrase; bench-edit-during-enforced-scope false attribution; review-genre null-final recovery) |
77-| C-044 | 2026-07-24 | NEG-8 drift-gate estimand debate (Ed-directed pre-ratification cross-model debate; Sol xhigh peer vs lead ruling) | Peer disagreed on inferential role (screen != stability proof) and was adjudicated CORRECT; Ed ratified the amended screen+budget design (option F full) with rigor-spiral + no-invented-physics guardrails; second recorded case of peer design judgment overturning a lead ruling pre-implementation |
78:| C-045 | 2026-07-24/25 | NEG-8 SCREEN+BUDGET audit gauntlet: four audit rounds and paired contract/execution refuters | PR #85 merged after three fix rounds; the paired lenses materially changed triage, and the residual custody-hardening work was queued |
79-| C-046 | 2026-07-26 | Retrospective: CAL-REBRACKET-01 max-bracket consumption gauntlet (PR #86) | Governed consumption-time authenticated re-derivation landed after three implementation rounds and three independent audits; a9/a10 replays passed with widened members and unchanged point estimates |
80:| C-047 | 2026-08-03 | The 16h runway (Ed-granted; joint Fable+Sol decision authority; concurrent sweep instance mid-flight): D-108/D-109 debate+rulings executed, D-110/D-111 sweep-triggered rulings, winB STOP cold gate -> D-112, two Sol gauntlets, pinned byte-identical mint replay, checkpoint for harness switch | D-108 closed via PR #99 + re-record; CAL-BRACKET held at 2e61ff9 (B1 residual, rule-11 gate owed); winB license exhausted as drawn (r06 disposition parked for Ed); mint chain D-110-blocked; CLAIMS_STATUS section 1 honestly NONE; sweep propagation fixes landed; layer yield in the run report |
81:| C-048 | 2026-08-04 | Integration-collision resolution on the CAL-BRACKET-D079-01 lead gate: bounded pre-decision Sol HIGH consult -> consult-shaped signature amendment -> fresh delta re-audit -> bench guard hardening -> merge-ref CI | The delta re-audit PROVED a live repr-'None' default spoof against the rendered-signature guard (hardened with a regression); the consult corrected the byte-identity oracle to integration-tree core-vs-wrapper parity (a historical-digest replay would have contradicted D-110); lead integration-tree replay 2487 OK exit-0 unpiped; PR #100 gate-complete, merged 2026-08-05 (`f75d12b`) |
82:| C-049 | 2026-08-05/06 | The 12h autonomous marathon: six PRs (#102-#104, #106-#108) + PR #109 issuance gauntlet; two rule-11 escalation consults (CGV F3 closure, QG census Option C); the D-079 issuance cold gate (split verdict, HOLD upheld); D-113/D-115/D-116; then the first re-mint consumption attempt exposed a structural closure -> Sol xhigh fork consult | The cold gate's HOLD prevented an irreversible ledger write paired with a production-refused artifact (F1 no-consumer-path, F2 digest-role coupling — issuance reframed as implementation and re-gauntleted as PRs #108/#109); xhigh delta re-audits again caught introduced defects (QG init-durability F1; CGV live-proved receipt-serialization B1 + phantom-fence B2); historical max-bracket consumption proved structurally closed at main — Option 2 (three fresh prospective windows) recommended by consult + magistrate; Ed's ruling OWED at close |
83-
84----
85-
--
100-  (fail-fast at idle_baseline, `permission_denied`, no fabricated
101-  baseline). Precedent: green tests are necessary, never sufficient —
102-  the blocker was invisible to a fully green suite.
103:(Amended 2026-07-08: the Opus-refuter tier was dropped at C-006 after
104:zero unique catches; refutation-as-protocol lives on with fresh Codex
105:refuters, as recorded in the adversarial-review evolution.)
106-
107-## C-002: Reverse review of the vertical-slice series; push vs PR
108-
--
117-  (Opus sweep + Codex independently convergent) — README/playbook test
118-  counts, phase-1 sudoers rows, phase-2 status paragraph contradicting
119-  its own matrix, PROJECT_STATUS blocked-items, wrong skip count, stale
120:  CI run number; (2) Codex-unique: the flagship config kept run_id
121-  `example-mac-mlx-local` across a workload-semantics change — explicit
122-  run_ids bypass hash suffixing, blurring provenance; (3) both reviewers
123-  independently: the committed sudoers line exposed the OS username.
124-  Commit hygiene otherwise CLEAN (messages match diffs, test-count chain
125:  reconciles, fixture justified, no secrets); CI risk assessed low
126-  (Codex ran the suite, config validation, and mock e2e itself).
127-- Discussion round (positions → resolution):
128-  - D1 flagship mutability: Claude held configs are entrypoints (run
--
138-    extension (prose status summaries carry an as-of date and defer to
139-    checklist matrix rows; no re-narrated gate lists) + a standing
140-    end-of-session docs-consistency sweep by a fast subagent
141:    (RUN_STATE end-of-work step 7). This session is the proof: the sweep
142-    caught everything the peer reviewer caught.
143-  - Push vs PR: Codex recommended branch+PR (one GitHub-readable diff +
144:    CI before main for a mixed code/config/docs series); Claude accepted;
145-    unanimous. Convention adopted for multi-commit sessions (D-031).
146-- Pre-PR blockers (all applied in the fix-up commit): staleness fixes,
147-  run_id rename + hash pin, `<local_user>` genericization of the sudoers
--
329-   (internal tool → published methodology → cross-lab table) written
330-   into the application entry. Dissent: none.
331-
332:5. **CI energy-regression gates — SCOPED with preconditions.** Attack
333-   (examiner #2, #7): run-to-run CV 0.3-1.4% today but across reboots /
334-   OS updates / charger states the variance envelope is unknown; a gate
335-   thresholded below the detection floor generates noise-failures and
--
370-
371-8. **Small-effect questions at n=5 — SCOPED with a power precondition.**
372-   Attack (examiner #2): sampling-strategy overhead, small runtime
373:   deltas, and minor DVFS effects are plausibly below the ~1% CI width
374-   n=5 buys at the observed CV. Reasoning: rather than dropping the
375-   questions, order them behind the detection-floor measurement and
376-   prescribe the rescue design (paired ABBA/interleaved runs, n=10-20
--
435-- Per-token energy claims and short-window phase joules (re-affirmed).
436-- Public cross-device leaderboards before wall calibration + cross-lab
437-  reproduction.
438:- Sub-detection-floor CI gate thresholds.
439-- Present-tense capability wording for queued features.
440-- (Re-affirmed standing kill) general intelligence-per-joule.
441-
--
458-  measurably paid off: it converted what would have been 8+ discussion
459-  rounds into direct adoption of pre-negotiated rewrites; zero follow-up
460-  Codex rounds were spent.
461:- Spend: 5 Codex lens invocations + orchestrator grounding/synthesis;
462-  no repo mutations (session shape B honored).
463-
464-
465-
466:## C-006 (session trace + meta-review, 2026-07-07): six-stream parallel batch, integration review, process meta-review
467-
468-Streams: A uncertainty/D-014 (in flight) · B campaign automation (merged,
469-PR #3) · C mock-hardening/P2-008 (in flight) · D rich-telemetry/P2-009
470-(merged, PR #4) · E kv-size helper (merged, PR #2) · F repo test-audit
471-(in flight). Plus: ideation council (DL-1) and a post-merge Codex
472:integration review over merged main.
473-
474-### Shape (orchestration decisions)
475-
--
500-    own the code).
501-- **Ideation council: 4 lenses + devil's advocate** — breadth beats depth
502-  for agenda-setting; divergence is the point (council skill, shape B).
503:- **Post-merge integration review added** because per-stream review
504-  structurally cannot see cross-stream interactions. Vindicated same
505-  session: it found 2 real interaction defects (K-9, K-10).
506-
--
516-| K-6 | rich-write failure aborted stop_sampling AFTER raw preservation | blocker | Codex counterreview (D) | implementer | mandatory counterreview | a parser bug destroys the very run it instruments — violates D-002's re-reduce promise |
517-| K-7 | runtime-clock anchoring broke regenerability-from-raw | blocker-class | test-AMPLIFICATION round (D) | implementer AND counterreview | amplification WRITES adversarial tests, doesn't just read | bundles not re-derivable from raw/ — core auditability promise broken |
518-| K-8 | lead's own verification run contaminated (agent-fleet display compositing held GPU ~75% busy) | measurement-validity | the idle-quality gate ITSELF (D) — its first true positive | the LEAD's prediction | building quality gates into the instrument | contaminated idle baseline blessed into the corpus; instrument outperformed operator |
519:| K-9 | stale-config glob landmine across streams | should-fix | post-merge Codex integration review | every per-stream review (structurally blind to it) | integration-review step exists precisely for this class | first mixed-stream run trips on stale configs |
520-| K-10 | unconditional per-rep env capture (cross-stream interaction) | should-fix | same | same | same | per-rep overhead inside measured runs |
521-
522-### Deliberations (design-bearing disagreements only)
--
561-| I-3 | one Codex lens wedged silently ~50 min (stdin hang: `codex exec` in background Bash without `< /dev/null`) | OUTSIDE evidence only: `ps` etimes + output-file mtimes vs finished siblings (agent reported nothing) | external kill; `< /dev/null` mandatory on every `codex exec`; fleet-health-check practice born (classify long-runners from ps/mtimes, never self-reports) | codex-delegation + multi-stream skills |
562-| I-4 | stream A accidentally stopped by the user | SendMessage returned "no active task" while siblings returned "queued" — a reusable stopped-stream detector | relaunch on surviving worktree state | this log (diagnostic recorded) |
563-
564:### Layer yield + spend (rough; spend capture starts next session)
565-
566-- Fresh-eyes Codex counterreview lenses: 2 unique (K-1, K-2) + 6 robustness
567-  (K-5, K-6). ~free (Codex quota).
568-- Fable orchestrator diff gates: 1 unique (K-3). Orchestrator context.
569-- Orchestrator live-verify vs real CLI: 1 unique blocker (K-4).
570:- Lead live-verify: 0 unique catches this session — but was itself CAUGHT
571-  by K-8; the layer's value this session was running the instrument that
572-  outperformed it.
573-- Test amplification: 1 unique real bug (K-7) + 14 edge tests (B).
574-- Fresh-instance test review: 6 vacuous/tautological tests fixed (B) + 2
575-  mutation gaps (D). No unique code bugs — on watch as a BUG-catch layer;
576-  clearly earning as a TEST-quality layer.
577:- Integration review: 2 unique (K-9, K-10) on its first outing.
578:- Opus refuter tier: not used this session; 0 unique catches for 2+
579-  sessions → drop from default roster per the council's own rule (C-006).
580-
581-### Doctrine changes (adopted this session, each folded same-session)
--
593-6. Explicit `model:` on every orchestrator spawn (I-2) (multi-stream).
594-7. Fleet health checks from outside evidence, on landing or ~hourly (I-3)
595-   (multi-stream).
596:8. Post-merge integration review is a standing step (K-9/K-10)
597-   (codex-delegation).
598-
599-### Meta-review C-006 verdicts adopted (same session)
600-
601-- Council log was HALF-INSTRUMENTED (catch attribution prose-only, zero
602:  spend records => drop-a-layer unenforceable). Fix: this entry is the
603-  first in trace format v2 (Shape / differential Catches / Deliberations /
604-  Interventions / Layer-yield); v2 + threshold adopted into the council
605:  skill. Spend capture starts next session.
606:- Opus refuter/verifier tier DROPPED from the default roster: zero unique
607-  catches since C-001; function absorbed by fresh-instance Codex
608-  counterreview + Fable gates. (The council's own evidence rule, applied
609-  to itself.)
--
628-  fixed (nulled + status; outlier kept with `modified_z: null`). **K-13**
629-  (C, orchestrator): review-lens over-strong assertion (all samples strictly
630-  interior) cut to the reducer's actual contract — the one genuinely flaky
631:  assertion removed before it could poison CI.
632-- **Deliberation blocks now on record** in the stream reports (quoted in
633-  full there; key adjudications): A's load-bearing disagreement — Codex
634-  refuted populating per-member `SummaryMetrics.uncertainty` ("structurally
--
756-    prototype-status banner + mock-path-first, three named drift fixes
757-    (AGENT_PLAN 2G/2H/2I checkboxes; Do-Not-Do-Yet desk-spike vs
758-    data-collection wording; playbook gate summary), slimmer M0 intake,
759:    RUN_STATE history trimming.
760-17. Execution order (next 5): P2-013 [AGENT] → P2-014 [AGENT] → P2-006 2M
761-    [QUIET-MAC] → Stage 3.0.1 spike [AGENT] → P2-010 → P2-012 [AGENT].
762-    Ed's parallel track [ED-EXTERNAL], explicitly flagged as a real
--
793-  queue item's acceptance is "all 31 pins flip"). Recorded as dissent, not
794-  consensus.
795-
796:### Per-layer catches (instrumentation)
797-
798:| layer | unique catches | notes |
799-|---|---|---|
800-| design lens (P2-013) | shared-summary-validator + shared-trace-path designs; B1 "present ≠ non-null" trap; cleanup ownership | shaped 3 consensus items |
801-| examiner lens (P2-013) | **raw-to-trace gap** (biggest catch); durable-evidence condition on A1; historical-corpus non-rewriting policy | major-revision verdict drove real scope change |
802:| planning lens | invariant-shaped commit groups; run_bundle_layout/checklist/council-log bookkeeping omissions; 7-not-6 audit test files; RUN_STATE staleness | beat the lead's grouping |
803-| architect lens | five seams break for Phase 3; three pre-2M contract amendments; composite-reader split note | overturned lead's PP6 |
804-| strategist lens | machine-state lanes ratified; 3.0.1-before-workload-buildout; "feature work stops" carveout; Ed one-pass external push | |
805-| project-examiner lens | detection floor confirmed unowned + concrete gate spec; phase-attribution-below-resolution objection; two-point scaling confound | supplied the "one change" (item 15) |
806-| docs lens | update-ledger scheme; index drift (C-005/C-006 missing — fixed this entry); three named drift items; slimmer M0 | |
807-| attack round (Codex, fresh) | A/B contradiction in lead's synthesis; B2 scope trim; Ed-burden flag; D-030 wording overclaim; 6 code spot-checks all confirmed | ratify-with-changes; all changes accepted |
808-
809:Spend: 8 Codex read-only sessions (~free per economics doctrine); lead
810-context spent on briefs, adjudication, and this record. Zero-unique-catch
811-layers: none — every lens landed at least one consensus-shaping catch.
812-
--
826-## C-008: Multi-stream session, checkpointed (2026-07-07 PM)
827-
828-Session entry (format v2), kept slim because the full Shape / Catches /
829:Deliberations / Interventions / Spend record was preserved VERBATIM as
830-`docs/run_reports/2026-07-07-checkpoint-session-trace.md`, and the
831-product state + restart instructions live in
832-`docs/run_reports/2026-07-07-checkpoint-multistream-session.md`. Do not
833-restate; read those.
834-
835-Pointer entry (per the C-009 recording rule): all product state,
836:process learnings, per-layer catches, and the calibration aggregate
837-live in the run report + its Process Trace Appendix. One
838-deliberation-class fact belongs here: the session's process conventions
839-(ledgers v2, calibration schema, decision-review doctrine) were shaped
--
862-  council log reserved for deliberation). In conferral Codex CONCEDED:
863-  "my earlier council-log-as-process-history position was too broad
864-  given the duplication evidence." Adopted: run report = the session
865:  record; council log = index rows + genuine-deliberation entries only.
866-- Codex amendments (accepted): bounded waits get a STALLED-handback rule
867-  (never infinite loops); retired ledgers leave a branch/hash pointer.
868-  Gap rule (Codex): every retired working artifact leaves a discoverable
--
883-- Consensus text: run report §"Meta-review consensus"; durable homes =
884-  the operation-loop + multi-stream-worktrees + codex-delegation skills
885-  (rewritten same-session). Migration executed same-session: trace
886:  merged into run report, RUN_STATE slimmed to pointer shape, queue
887-  cells slimmed, C-008 converted to pointer style, codex-run patch task
888-  queued.
889-
--
891-
892-## C-010: Resume + merge session — C-009 topology first full run (2026-07-07/08)
893-
894:Pointer entry: all product state, the per-layer catch/yield table, the
895-delegation-calibration aggregate, and restart instructions live in
896-`docs/run_reports/2026-07-07-resume-merge-session.md` (Process Trace
897-Appendix included). PRs #8/#9/#10 merged (Ed-directed, after a
898:3-reviewer pre-merge oversight pass with lead triage + 5.5 fixes);
899-PR #11 open. Deliberation-class facts for this log: (1) the lead-driven
900-codex-run topology ran a full session with ZERO wake stalls and zero
901-heartbeats — the C-009 T1 hybrid is validated on its pipeline half;
--
904-faithfully pinned the broken shapes — fixture-first streams now always
905-carry the full lens tier (folded into multi-stream-worktrees);
906-(3) a volunteered 5.5 addition (vLLM provenance) was rejected at the
907:lead diff gate for hashing fabricated token IDs as realized evidence —
908-first clear model-defect row in the calibration ledger; the correction
909-(node-realized IDs via /tokenize or structured absence) is ledgered
910-B-44 with D-033 pressure intact; (4) K5's audit pin was adjudicated
--
1001-consumer audit, adversarial confound hunt), lead triage with
1002-dispositions, one Codex peer counterreview of the full synthesis with
1003-design judgment explicitly invited, lead adjudication. Design docs
1004:implemented by a pinned Codex session; lead diff gate before commit.
1005-
1006-Convergent blockers (lead + all three lenses independently): Q4
1007-unreachable at L3 from the 2M 4-cell grid; P2-015's absolute floor is
1008:not the comparative MDE that gates L2/L3 claims. Unique catches by
1009-layer: skeptic — jw_mixed category x shape confound (the C-W.1 null was
1010-unfalsifiable as designed), silent long_short cap divergence, drift
1011-sentinels, content-sensitivity sentinel promotion; power — the MDE
--
1020-(1) P2-010 splits into substrate + smoke ladder, full scored campaign
1021-deferred — amends C-004's packaging; peer AGREE. (2) jw_mixed_v1 runs
1022-phased with a common-shape identification stratum — supersedes C-005's
1023:fixed-budget-full-first sequencing; peer AGREE ("spend-before-
1024-identification"). (3) Quiet-window packing: lead leaned one window; peer
1025-OVERTURNED to two (MDE-sized n cannot precede the floor campaign; a 4-6h
1026-single window raises drift risk exactly while establishing a floor) —
--
1041-lead designs overturned with strictly better ones (grid, window
1042-packing), consistent with the 2026-07-07 calibration signal that
1043-design-freedom delegation to 5.5 runs hotter than doctrine assumed.
1044:Every layer produced unique catches this session; no drop candidates.
1045-
1046-## C-015: Benchmark expansion council — suite architecture v2 + interop (2026-07-08)
1047-
--
1072-metadata); interop direction (D-041 — thin import manifests, HumanEval
1073-smoke first, marker-shim energy layer with a verdict-shaped spike,
1074-export prioritized for adoption-per-build-day, kill list). Peer's
1075:unique catch: PER-ITEM FAILURE ECONOMICS — without a per-item
1076-validity/status model + aggregation rules, suite breadth creates
1077-ambiguous partial evidence; adopted into the P2-010a substrate
1078-definition. Peer also drew the capstone stop-line (guaranteed capstone
1079-= instrument + Mac characterization; expansion drops first under
1080-pressure) and restated the D-034 gate — both landed in the 2O plan.
1081-
1082:Layer yield note: all four lenses + peer produced unique catches;
1083-the invited-peer pattern again narrowed designs materially (minimal-
1084-substrate cap, energy-layer-only pin, gate amendment). Zero dissent
1085-recorded; the round's three open design questions (substrate scope,
1086-import-vs-export priority, capability-map home) resolved in one
1087-counterreview pass without a second discussion round. A post-landing
1088:verification workflow (3 lenses + refuters) then caught one blocker
1089-(the 2O section retaining the superseded C-014 substrate enumeration)
1090-and six should-fixes (level-marker omission vs AP-5, D-039-allowlist
1091-drift worded as restatement, lossy D-041 kill-list record, an inflated
--
1109-decisions → fresh Codex adversarial round on the decision batch →
1110-implementation in 3 streams (substrate 3 units; affine; generators) each
1111-with 2-3 fresh lenses + fix rounds → 1 Opus fresh-eyes substitute during
1112:a Codex quota outage → 7-reviewer pre-merge oversight → 3 final-head
1113:passes → post-merge integration review. Full narrative + per-layer catch
1114-rows: `docs/run_reports/2026-07-08-suite-build.md` (process trace
1115-appendix).
1116-
--
1125-dedicated-sentinel-item shape over relaxing SUB-1 (D-047.2 amendment,
1126-k=25/26).
1127-
1128:Layer yield (unique catches): lead live gates 3 (all
1129-integration-reality class: cwd refs, strict rollup provenance, sampler
1130:API namespace — invisible to 680+ unit tests and 9 lenses); oversight
1131-10+ (incl. two validation holes: tamperable rollup digest,
1132-vanishing group markers); unit lenses ~20; Opus substitute 1 major
1133-(tokenize-window bracketing, FakeClock-blind); adversarial adjudication
--
1146-
1147-## C-018: D-013 alignment-capture window fix (2026-07-08)
1148-
1149:Shape: background-chip session for the C-017 oversight spin-off
1150-(alignment capture inside the measured window; predates the suite
1151-substrate, since de5f04a). Solo lead implementation — a two-line
1152-reorder in `_stage_measured_run` (stamp `sampling_stopped_s` as soon
--
1156-read-only review of the final diff (timing-semantics-adjacent, so the
1157-cross-model pass ran despite the small size; no council per rule 3).
1158-
1159:Layer yield: the catch itself is credited to the C-017 oversight
1160:layer. This session: lead live verification proved both tests fail
1161-pre-fix (gross_energy_j 0.84 -> 38.34 J under a 5 s simulated capture
1162-cost) and re-ran the full suite (734 green); Codex review returned
1163-approve with zero findings (it independently re-checked
--
1187-- CALIBRATION LONGITUDINAL: design-freedom-runs-hot confirmed across
1188-  C-010/C-014-15/C-017 (high judgment yield, gates still mandatory); no
1189-  active layer at two consecutive zero-catch sessions; WATCH items:
1190:  integration-after-clean-oversight (one zero at C-017, C-010 contra),
1191-  Opus-vs-Codex fresh-eyes A/B (sealed same-packet protocol defined; ≥2
1192-  trials before roster change). Prompt-defect class active (~2/large
1193-  session, lead-side); quality denominator (false-positive burden,
--
1200-  work. R-012 schedule risk named the biggest active management risk;
1201-  R-016 interim backup becomes serious before 2M.
1202-- CLOSURE: D-013 prose/docstrings back-annotated to marker-bounded
1203:  wording (this batch); C-018 index row added with commit hashes;
1204:  RUN_STATE 734; bank affine-queued line amended. Derivability clean.
1205-- CRITIC dispositions: (1) sealed A/B re-baselining ADOPTED (skill);
1206-  (2) pre-#21 bundle validity — alignment-capture overhead is
1207-  dict-read-scale, corpus remains claim-usable, recorded here, no
--
1317-- Keep generated static pages as the audit fallback; do not make Lakebed a
1318-  parallel project-status database.
1319-- Add `/api/live-status` as a fail-soft overlay parsed from current GitHub
1320:  markdown for `PROJECT_STATUS.md`, `RUN_STATE.md`, `TASK_QUEUE.md`, and
1321-  `docs/risk_register.md`.
1322-- Expand the generated status cockpit with advisor attention, campaign
1323-  readiness, evidence, and claim-ceiling panels.
--
1369-  pre-hardware work plan (headline first, P2-015 as combined
1370-  floor+calibration+trust+error-budget spec, stats amendment before
1371-  reducer code, campaign packs last behind a registry/linter cut-line).
1372:- Unique catches by layer: L1 error budget + idle-model + phase-gate;
1373-  L2 multiplicity + contrast-rule + ordering gap; L3 registry gap +
1374-  per-question table + coverage gaps (telemetry perturbation, version
1375-  drift, jitter sensitivity, output-token identity); L4 frozen headline
--
1392-amendment + analysis registry, canonical RQ registry), each with a fresh
1393-read-only counterreview lens, FIX-N rounds for accepted findings, a fresh
1394-final-head pass per branch, a tail-verification pass over post-review
1395:commits, CI, self-merge under the standing authority, and one post-merge
1396:integration review (5 seam findings, fixed same-session).
1397-
1398-Dissent: none unresolved. Notable adjudications: R2 estimator kill
1399-accepted (floor redefined as false-effect guard); FH ledger-promotion
--
1421-
1422-Shape: first Workflow-orchestrated build (46 agents: 4 codex implement
1423-streams in worktrees -> 2 lenses each with stream-specific angles ->
1424:severity-tiered adversarial refuters: blockers 2, should-fix 1) plus two
1425-lead-driven reinforcement streams (claims linter pulled forward from the
1426-cut-line; RQ-ENERGY-VARIANCE candidate design from Ed's variance
1427-question), then per-stream fix rounds, lead gates (suite + live e2e on
1428-the lead's shell, incl. strict-validating live rotated campaign
1429-bundles), 6 fresh final-heads, a combined tail-verification pass, a
1430-throwaway combined-ref merge + full suite BEFORE merging (C-022 lesson,
1431:first deliberate use), CI, self-merges, and one integration review with
1432-live rotated-campaign interaction checks.
1433-
1434-Notable: the design-round-first flow (Ed's directive, folded to
--
1487-- ARCH severity: undifferentiated blocker trio split into immediate
1488-  (zero-window, P2-040) vs NVIDIA-gated (NV-GATE-2) per counterreview.
1489-- Sequential sampling: fixed-n + explicit demotion adopted over both
1490:  status quo and default alpha-spending (D-062); peer confirmed the
1491-  demotion rule is coherent only with its four explicit clauses.
1492-
1493-Layer yields (C-027): lenses 8 confirmed blocker clusters + ~60
--
1511-
1512----
1513-
1514:## Index row
1515-
1516:| C-028 | 2026-07-09/11 | C-027 adjudication → integration arc under the Fable-lead / gpt-5.6-sol division of labor (this segment: infrastructure wave + PRs #49/#54/#55 + integration window) | PRs #49, #54, #55 merged mid-arc; held wave #50–#53, #56–#58 integration-reviewed and merged (SHA-guarded) after the integration tree caught 38 cross-stream failures pre-merge; follow-up PR #59 opened from the cross-stream review; refuter tier narrowed 2 blockers via contradictory verdicts; delta re-audits caught 2 fresh blockers in newly-reachable paths; claude-codex-report/v1 + codex-run-v3 + WRITE_SCOPE backstop + NEEDS_RULING adopted (D-064); ~57 recorded Sol invocations |
1517:| C-029 | 2026-07-11/12 | Agent-lane triple (SITE-01 / P2-049 / P2-028): three standard-tier Sol pipelines, per-stream lenses, lead bench adjudication of 5 blocker claims (2 confirmed, 1 partially refuted, 1 design ruling, 1 reproduce-first — refuters replaced by lead code-reading where cheaper); trace + calibration table in `docs/run_reports/2026-07-12-agent-lane-triple.md` §Process Trace Appendix (the ONE home; no full entry here) | PRs #61/#62/#63 opened at lead-gated heads; lead-gate unique catch: fix round's `succeeded`-only rule would refuse legitimate `capped` cells (FIX-14; third "fix rounds introduce defects" datum); implementer caught a stale kernel authority pointer (half-right — lead archaeology completed it, `507f600`); process defects logged: WRITE_SCOPE in-prompt requirement (3 rc=64), unintended ULTRA effort on all 13 invocations (config passthrough; TOOL-01), upstream outage killed 3 delta-audit attempts (re-audits owed pre-merge on #62/#63) |
1518:| C-030 | 2026-07-13 | Restart close (continuation of C-029; Ed-authorized merges): delta re-audits on #62/#63 finals + post-merge integration review, all explicit xhigh (effort fix held: 3 sessions ≈ 7.0M tokens vs the prior 13 ≈ 118M); two lead bench fixes with defect regressions; trace in `docs/run_reports/2026-07-13-restart-merge-deploy.md` (the ONE home; no full entry) | #61-#63 MERGED; delta-audit unique catch DRA-001 (equal-but-malformed identity hashes counted as identity evidence — fourth "fix rounds introduce defects" datum, this one surviving TWO earlier review layers); integration-review unique catch XSI-1 (installed-wheel CI ran only --help; now smokes both new fail-closed surfaces); lead-live layer: deploy ACCEPTED 854,349 B / routes 5/5 / freshness clear + cross-thread breakage fix (P2-028 kernel retirement vs gen_state fidelity tests, caught by the concurrent bridge thread's suite run); concurrent Claude↔Sol bridge landed same tree, lead-verified 8/8 protocol + 4/4 tests before commit; PAUSE: comprehensive whole-project audit declared next gate (Ed) |
1519:| C-031 | 2026-07-13 | Bridge v1 (Ed-directed): 3-round Fable<->Sol design discussion held OVER the MCP bridge itself (thread 019f5a67-00f5); Sol out-designed the lead 3x (hard-block leases vs warn-only, path-level baseline manifests vs status digest, split event logs) — all accepted; 5 draft-choices lead-adjudicated; impl + 2 fix rounds + fresh lens + delta re-audit; full record `docs/run_reports/2026-07-13-bridge-v1.md` (the ONE home) | PR #64 MERGED: bridge-protocol/v1 contract + scripts/bridge (atomic hard-block leases — direct fix for the 2026-07-12 cross-thread collision — baselines, 4-verdict scope-check, thread registry) + adapter FAILED-synthesis; lens caught 4 blockers, delta re-audit caught 1 NEW blocker (malformed-override fail-open; FIFTH fix-rounds-inject-defects datum); audit-loop termination ruling: post-fix2 residue lead-verified directly; suite 1358 OK |
1520:| C-032 | 2026-07-13 | Bridge v1.1 (Ed-directed: "fix up the bridge for maximum co-work"): Sol xhigh design consult over the bridge (thread 019f5d1d-b681-7db1-8714-812fdd2f198b; 5 amendments accepted + v1 duplicate-sentinel adapter bug confirmed); ratified spec Sol-implemented; 3 lenses → 3 fix rounds → 3 delta re-audits, finding convergence 13→6→2→1; full record `docs/run_reports/2026-07-13-bridge-v11.md` (the ONE home; no full entry) | PR #65 MERGED `d285989` (Ed named the merge same session after the harness declined agent self-merge): discussion lane, receipt-anchored session-open/close wrappers (session.lock-serialized, write-only in v1.1), tolerant envelope, per-call reverse effort + echo, peer channels + bounded proposal diffs, one-home effort dedup; delta re-audits caught 6+2+1 fix-round findings (sixth/seventh "fix rounds introduce defects" data) incl. two corrections of the lead; suite 1387 OK; CI green on final head 8b96bd4 |
1521-| C-035 | 2026-07-15 | AXI spec-design phase (Ed: "design as many specs as you can with help from sol"; arc opened post-clearance with predeclared deliverable per WO-022 §5a): three parallel Sol spec pipelines (SA xhigh / SD high / SE xhigh), each author -> fresh counterreview -> fix round(s) -> delta -> lead termination; ~14 Sol sessions ≈ 71.2M tokens (est.); full trace in the 2026-07-14 run report §AXI spec-design phase | Specs landed `1464c93`/`d2bd5ee`/`3b5c4bf`: SA burst-decode contract (implementation-ready; honest frozen-arm goldens after the counterreview refuted byte-identical vs actual code; deterministic anti-top-up ledger), SD pair scorecard (four-option D-016 decision box for Ed; forced-continuation memory probe), SE six AP drafts (estimand demotion on AP-REASON-VARIANCE; union-bound + Markov-quantile floor guards; 21 PROVISIONAL cells with named triggers); 30+ counterreview findings fixed pre-landing; 3 benign lease-close artifacts pending Ed batch adjudication |
1522:| C-034 | 2026-07-14/15 | Audit fix-wave resume + close-out (Ed's AXI handoff §0.2 sequencing; full record `docs/run_reports/2026-07-14-audit-resume-axi.md`, the ONE home): per-order cadence Sol high/xhigh implement → fresh checker → fix rounds → lead gate; 28 Sol sessions ≈ 251M tokens (ARC HARD crossing recorded in the refreshed WO-022 receipt — gate-closing work, policy landed mid-arc); ULTRA comparison audit (intended, pre-declared) + xhigh integration review + Fable completeness critic + C-033 coherence council | S1 closed (WO-010 NEEDS_SCOPE grant, WO-011 checker-FAIL→fix→delta-PASS), S4 closed (WO-019 PASS-0-findings; WO-031 3-major fix round), WO-027 fix round, WO-021 xhigh 3-phase w/ 8a receipt + 4-record-loss BLOCKER migration, WO-022 verbatim landing; integration tree `impl/audit-integration`: 2 unique integration catches (capsule budget union breach; D-068 vacuous-green surfaces) + ULTRA's 2 blockers/20 findings triaged per Ed's substance-over-ceremony ruling (7 fixed `913a2a6`, 4 bench, 5 queued, rest dispositioned §8.5); D-043 closure (17 lines + 6 lead decision-log amendments); critic's 3 gaps closed same session; suite 1532 OK at `f8f0f92`; PR to main awaits Ed's adoption merge; 3 lease adjudications Ed-approved after classifier refused lead self-approval (correctly, all three times) |
1523:| C-033 | 2026-07-14 | AXI intake council (Ed-directed via `docs/axi-handoff.md` + Ed's batched §5 answers this session): short recorded Sol high read-only coherence review of drafted D-066..D-070 (outcomes Ed-directed, not re-decided; consult ran over the audited CLI path because the MCP server is unavailable in this headless session; prompt/response tracked at `docs/process_traces/2026-07-14-c033-axi-consult/`) | Sol verdict DISCUSSION: outcomes authorized, Ed's four D-067 amendments honored; 6 coherence corrections identified and ALL lead-accepted before commit: explicit supersession of the D-058 token-normalization Primary Metric clause (contract text assigned to S-A, keeping S-0 docs-only), dual-basis-capture bundle-state definition (successful idle-eligible request-level; nullable semantics preserved), D-032 gross-only phase semantics named, deploy convention re-attributed C-012→C-013, registry source homes corrected (C5-* bank vs C-023-*/RQ-* registry per D-055), `request_id` pinned to `events.jsonl` `metadata.request_id` with new-version-only reducer dispatch, D-064 duplicate/mismatched index rows cleaned; remaining deploy-instruction surfaces routed to WO-031 + S-0 |
1524:| C-037 | 2026-07-17 | Window-A execution + wrap arc (Ed: floors-first overnight -> advisor deadline -> site rebuild -> exploratory breadth; full records: the two 2026-07-16/17 run reports, the ONE homes): four-failure shakedown story (stale-bundle reuse, wallpaper idle contamination caught by sentinel, 34.6ms trace-boundary bracket via two live-bundle triages, stale-lock exit-0 wart) -> canonical PASS; 248-line/222-bundle floor campaign verified by 8-agent ultracode extraction; advisor brief + README-first site + Learn guide (Ed deployed); exploratory 9-bundle block; DSpark/DFlash feasibility confirmed; D-071..D-075 recorded | PRs #72-#75 merged under D-072 standing authority; delta re-audits caught blockers twice more (10th datum incl. lead-pinned formula defect); fold-in round's refusal caught a forced-report placeholder trace; scope enforcement caught the lead's own stray file (adjudicated benign); floors: request 0.527/0.052 J, phase 1.477/0.786 J, ABBA comparative w/ flagged tail drift; exploratory gross suite: OLMoE ~229 J vs Qwen3-4B ~362.8 J vs 122B ~1072 J (exploratory-labeled) |
1525:| C-036 | 2026-07-16 | Resumption + no-hardware batch (Ed: audits in a workflow + "handle the merge yourself if all is well... get the project ready for my quiet mac"; full record `docs/run_reports/2026-07-16-resumption-nohw-batch.md`, the ONE home): ultracode readiness workflow (4 Sol-high audits + severity-tiered refuters) BEFORE work selection; then 4 streams (SPLIT-AP xhigh contract tier, SITE-02 high standard, AXI-SB xhigh spike, AXI-SD Fable web-verification); every fix round delta-re-audited; three self-merges under Ed's in-session delegation, each with the full D-031-amended gate | PRs #67 (`7593259`, AXI-SA + CI portability fix after the audit caught red CI), #68 (`2778ed2`, SITE-02 — D2 step verified EXECUTED in the CI log), #69 (`9db4546`, SPLIT-AP freeze) merged; integration review 0 cross-stream defects, merged main 1630 OK; kernel closures 51→48 IDs; AXI-SB live probes (lead-run, B∈{2,4}) → verdict `supported`, Mac C5-2.2 leg mint staged on `impl/axi-sb` (effective on its merge); delta re-audit caught a LEAD-pinned predictor defect (8th fix-rounds-inject-defects datum, first lead-authored); AXI-SD memo: OLMo pair d_active 0.0016 + 8GB-fit may moot Option A's premise, Qwen3 pair confirmed-fails G10 (17.17 GB) |
1526:| C-039 | 2026-07-28 | Mint-implementation session (Ed: resume per RUN_STATE, then "merge on green + start the mint consult"; magistrate topology; full record `docs/run_reports/2026-07-28-floor-mint-implementation.md`, the ONE home): PR #87 gauntlet (2 Sol xhigh lenses + 5 Sol high refuters + 1 Opus contract refuter, lieutenant-directed), E4 fix + CLEAN delta re-audit, D-081 parser ruling (Ed, async question), Sol xhigh mint design consult (3 DISAGREEs sustained -> D-082), 7-stage xhigh implementation, suite-pruning consult (0 removals clear D-061) | PR #87 MERGED `058c918`; `impl/mint-tool` pushed unmerged (review owed); C1 SPLIT (Sol nit vs Opus should-fix) magistrate-synthesized to should-fix, closed via ratified Q4; 5 broken-wake incidents -> tracked-poll pattern folded to codex-delegation; lieutenant self-flagged 2 retracted fabricated verdict narrations (mechanism removed); concurrent-session force-push anomaly flagged to Ed; **ADDENDUM at the end of this file** records the 2026-07-29/30 continuation (FIX-6..9 gauntlet, three cold gates with paired Opus contract-lens refuters, mint #1, the 7B floor window; rulings D-083..D-088; D-088 recorded in the same-day close-out); **ADDENDUM II** records the 2026-07-30/31 escalation consults (cooldown-join design consult → D5-J/D-089; contrast-window recovery consult, the first trigger firing inside a measurement window) |
1527-
1528----
1529-
--
1542-entry records the 2026-07-10/11 continuation.
1543-
1544-Participants: Fable lead; gpt-5.6-sol as implementer, reviewer,
1545:refuter, auditor, and design consultant across ~57 recorded
1546-invocations. The lead retained worktree/merge authority, every final
1547-diff gate, all live verification, and bookkeeping.
1548-
--
1574-
1575-Layer structure: Sol implementation sessions (xhigh; 2 ultra for the
1576-p2041-vetted composition and the P2-037 engine) → review lenses
1577:(contract + semantics per stream) → severity-tiered refuters (2 per
1578:blocker) → independent post-hoc audits (P2-037) → delta re-audits
1579-after fix rounds → lead gates (live runs, arithmetic checks, final
1580:heads, CI) → cross-stream integration tree before each merge.
1581-
1582:Unique catches per layer (D-061 evaluation record):
1583-
1584-- **Sol merge review:** caught the lead's own merge-resolution
1585-  error — the branch's updated P2-005 row silently lost by a
1586-  whole-file `--theirs` checkout during the #49 conflict
1587-  resolution; repaired as a proper 3-way merge (`13f6c9e`). Only
1588-  layer to catch it.
1589:- **Refuter tier:** narrowed 2 blockers via CONTRADICTORY paired
1590:  verdicts — P2-041 B1 (contract refuter confirmed, reachability
1591:  refuter refuted the broad form → landed as the narrowed shared
1592-  fail-closed cooldown verifier, `f2c4701`) and P2-037 F1 (design
1593:  vs repro refuters split the same way → F1 narrowed before the
1594-  fix round). The disagreement itself was the signal; neither
1595:  single refuter would have produced the narrowed form.
1596:- **Delta re-audits:** 2 fresh blockers in paths newly reachable
1597:  only after the fix round (P2-037 delta re-audit:
1598-  blocker=2/should-fix=3), plus the recurring symlink pattern —
1599-  cooldown provenance `Path.resolve` unwrapped against symlink
1600-  loop/OSError, wrapped fail-closed with a cross-version
--
1624-recovery row rather than a mutated record — both behaviors are now
1625-ratified in D-064.
1626-
1627:Rough spend (from the two manifests + local usage accounting;
1628-estimates, not billing truth): 2 ultra sessions ≈ 100M tokens
1629-(p2041-vetted composition, P2-037 engine); 53 recorded xhigh
1630-invocations (14 v2-manifest + 37 v3-event-stream + 2 transition-era
--
1634-~570M cache reads. Two v3 sessions (doc008-r3, pr59-review) still
1635-RUNNING at the manifest snapshot.
1636-
1637:Spend snapshot addendum (2026-07-11 ~20:00Z, `codex-usage` 24h
1638-window, arc-close truth for the table above; estimates, not billing):
1639-59 Sol sessions / 330.6M tokens / ~17.5h session time — xhigh 55 ≈
1640-190.4M, ultra 2 ≈ 100.3M, high 2 ≈ 40.0M (both FAILED). Composition
--
1671-argued — it was triaged per-file and rebuilt from main under three
1672-Ed-approved C rulings (`96e10bd`, `750f7d0`).
1673-
1674:Calibration note (model-version scoping, per C-027): the refuter
1675-contradictory-verdict pattern produced correct narrowings twice;
1676-the two scope violations and one thin-output ultra warning are the
1677-arc's recorded 5.6-sol failure modes. Sealed A/B remains the gate
--
1680-## C-043: D-078 P0 instrument-repair close-out session — round-8 landing, round-9 final confirmation, sign-off (2026-07-22)
1681-
1682-Shape: lead resumed the paused arc cold from scratchpad pointers; collected
1683:the checkpointed Sol round-8 fix wave; §C-028 delta re-audit (3 fresh
1684:read-only Sol lenses over a shared packet → 8 xhigh refuter verdicts,
1685:blockers 2 refuters with distinct lenses); Sol xhigh round-8b fix wave under
1686-enforced WRITE_SCOPE (one NEEDS_SCOPE early-return, lead-ruled, fixture fix
1687:applied at the bench); bounded 8b delta re-audit; lead full-suite gates
1688-(2081 → 2088 passed, 0 failures); commit `040ca3a`; round-9 FINAL
1689-confirmation (Sol xhigh review genre); CR9-1 adjudicated as registered
1690-limitation L1 per the loop-termination doctrine; close-out `debc6d2`;
1691-PR #79 opened for Ed-named merge.
1692-
1693:Layer catches (unique):
1694-- Sol review lenses: A1 (v3 claim-eligibility contract divergence),
1695-  B1 (ClockStamp physical-sanity gap → understated B_fiducial ~3 µs),
1696-  C1/C2 (boundary float, OverflowError escape), C3/C4 (test-wiring gaps).
1697:- Sol xhigh refuters: killed A2/B2 outright (both plausible, both wrong —
1698-  A2's "legacy records break" was self-invalid synthetic-only; B2's
1699-  stale-vs-invalid relabel would have broken a ratified distinction);
1700-  narrowed C1 to a registered nit; split on A1 (contract-confirmed,
--
1706-  (both were the lead's own authorized bench edits); the L1 adjudication.
1707-
1708-Failure modes recorded: (1) upstream cyber-content filter killed 3/8
1709:refuters mid-run on adversarial phrasing ("malformed/tamper/escape") —
1710-rephrasing as data-quality QA of our own instrument recovered all three
1711:(route: keep refuter briefs mechanism-neutral); (2) lead bench-edited the
1712-worktree while an enforced-scope Sol session ran in it → false
1713-SCOPE_VIOLATION attribution + resume-registry loss (rule: no lead edits in
1714-a tree with a live enforced-scope session); (3) the known xhigh review-genre
--
1739-design yield than review-shaped prompts; adopt as the default shape for
1740-estimand/contract rulings.
1741-
1742:## C-045: NEG-8 screen+budget audit gauntlet — a new refuter pairing under A/B, four audit rounds, PR #85 (2026-07-24/25)
1743-
1744-Shape: the Ed-ratified SCREEN + BUDGET wave (D-078 clause 10) was taken
1745-through four adversarial audit rounds (fresh read-only Sol per round;
1746:rounds 1–3 xhigh, round 4 high) with per-severity refuter tiers using a
1747-NEW pairing under evaluation — **Opus-contract + Sol-execution distinct
1748-lenses** (Ed-directed A/B; now the recorded default per the
1749-instrument-mix-authority memory). Three Sol fix rounds (xhigh, xhigh +
1750:a high alignment pass, high) plus lead bench fixes closed the findings;
1751-two lead-owned decision-log addenda were written at the bench between
1752-rounds. Commit stack on main(`125a48d`): `b120d07` wave → `69b65e5`
1753-addendum 2 → `ad75542` fix round 1 → `315810a` addendum 3 → `a5a7acf`
--
1755-`19e15d9` assertion restore → `60b12af` capsule pagination →
1756-merged `c3e2647` (PR #85, 56 files, +6012/−439).
1757-
1758:Layer catches (unique):
1759-
1760-- **Auditor (fresh Sol, per round):** found real mechanisms in every
1761-  round — round 1: estimand-dispatch downgrade (row shape selects the
--
1771-  barrier, and loss of nonempty positive-path integration coverage;
1772-  round 4: two omitted assertions in the replacement companion
1773-  (nonempty affected-contrast set, `n == 5`). BUT it severity-inflated
1774:  repeatedly — of 7 blocker-tier claims across rounds 1–2, refuter
1775-  synthesis sustained 3–4 at tier (round 3 and round 4 produced no
1776-  blockers at all: three should-fix, then one).
1777:- **Opus-contract refuter (unique):** F2 collapse (the "broken frozen
1778-  replay" blocker rested on a misreading of the freshness addendum's
1779-  scoping — landed as a documented superseded gross-only wire, not a
1780-  code fix); F6 refutation (condition-level distinctness was already
--
1791-  sentinel route on round-3 F2 (the one route with no downstream
1792-  catch); and the F3 fixture-fix refutation (a production-promoted
1793-  fixture cannot be strict-valid — use a patch idiom instead).
1794:- **Sol-execution refuter (unique):** discovery of the
1795-  coordinated-downgrade *variants* (strip the drift group and restore
1796-  the headline floors and the record validates clean — reproduced on
1797-  the repo fixture, gate `20.799350577898302 → 20.399350577898304`,
--
1815-  fallback-anchored member, r03; true floor ≈ 3.3–3.7 J), and the
1816-  terminal mock bar; severity synthesis on the split verdicts (kept F4
1817-  at blocker priority on imminent-use grounds against the contract
1818:  refuter's downgrade); the capsule shard-budget trim (`a5a7acf`) and
1819-  the pagination ruling that followed (deterministic `D-NNN`
1820-  pagination + D-076 artifact-cap redirects); the battery-flake
1821-  adjudications; and the bench fixes (registry clause, the fixture
1822-  metadata line that blocked Sol's canonical run, the round-4
1823-  assertion restore).
1824-
1825:Rough spend (estimates, not billing truth): the gauntlet proper (audit
1826-round 1 onward) recorded 11 distinct Sol wrapper invocations — 4 audits
1827:(3 xhigh, 1 high), 2 execution refuters (both high), 3 implementation
1828-rounds (xhigh; xhigh + a high alignment pass; high), 1 capsule session
1829-(xhigh), plus retry attempts on two of them; counting the same day's
1830-pre-audit wave, fold, fold2 and run-book sessions brings the day's Sol
1831:total to ~15. Four Opus agents: three contract/design refuters (~96k /
1832-120k / 144k tokens) plus one dictated-fills drafting/verification agent
1833-(~115k) — the latter caught five material errors in the lead's own
1834-dictation of this entry, including the effort-tier discrepancy ruled on
--
1844-never saw (A1 terminal mock bar). The two lenses split on G1/G2 (Sol
1845-sustained both at blocker; Opus re-priced both) and the lead synthesized
1846-rather than majority-voted, per §C-028. Adopted as the default
1847:blocker-refuter shape; memory and skills to be updated by the lead.
1848-
1849:Dissent recorded: on F4 the lead overrode the contract refuter's
1850-downgrade and kept blocker priority, on the grounds that the
1851-anchor-fallback replay path was about to be exercised by the next
1852-window's re-verdict. On G1/G2 the lead implemented both fixes despite
--
1856-Calibration note: the auditor layer's yield is real but its severity
1857-calibration is not — four consecutive rounds produced findings worth
1858-fixing while its blocker tier held at roughly half strength. The
1859:refuter tier is what converts that into correct triage; running a
1860:single-lens refuter would have inherited the inflation.
1861-
1862-Effort-tier ruling (lead, flagged by the drafting agent's verification
1863:pass): the execution refuters ran at `high`, not the
1864-adversarial-review skill's `xhigh` default — deliberately in round 1
1865-(Ed's A/B spec named "sol high") and carried into round 2 for
1866:comparability. The A/B verdict therefore stands on high-tier refuters,
1867-which is the STRONGER form of the result: paired distinct-lens
1868:refuters at high changed triage outcomes that single-lens xhigh
1869:refuters have historically missed. Ruling: in the paired-lens shape,
1870:`high` is the default refuter tier; reserve `xhigh` for single-refuter
1871-verification or judgment-dense standalone audits. The lead will amend
1872-the adversarial-review skill's effort note accordingly.
1873-
1874-Scorecard (dispositions per docs/orchestration.md): 20 findings raised
1875:across 4 audit rounds incl. refuter adjacents. Accepted-and-fixed in
1876-PR #85: 13 (r1 F1/F3/F4/F5/F7; r2 G1/G2/G3 + adjacent A1 terminal mock
1877:bar; r3 F1/F2/F3; r4 F1). Re-priced by refuters before fixing: 4 of
1878-those (r1 F4 blocker→should-fix; r2 G1/G2 blocker→should-fix; r1 F2
1879-blocker→docs-only, landed as contract clarification). Rejected /
1880-non-obligating: 2 (r1 F6 contract-refuted; r2-A2 traced not-reachable,
--
1892-
1893-Shape: finish the FLOOR-LABEL-01 gauntlet (D-078 clause 11 — labelled
1894-attribution-limited floors, unblocked by CAL-REBRACKET-01 / PR #86) and
1895:then spend the quiet-Mac window collecting three measurement windows.
1896-Lead instrument: **Opus 5 (1M context), effort `high`, confirmed by Ed
1897-via the interactive `/model` command** (the TUI banner disagreed; see
1898-`docs/process/model_allocation_ledger.md` §6 A-10). Mid-session Ed
--
1903-`instrument-mix-authority` memory and in the ledger §2 — this entry is
1904-the first session run under it.
1905-
1906:### Layer catches (unique)
1907-
1908-- **Opus 5 contract lens** (subagent; ~164k tokens, 50 tool uses,
1909-  ~11 min). Verdict **"COMPARATIVE COVERAGE: COMPLETE"** — it traced
--
1978-  promotion on the grounds that it would operate the same harness with
1979-  the same wake semantics.
1980-- **Lead (Opus 5) bench catches:** detected that its own suite
1981:  verification was **worthless because it piped output through `tail`**,
1982-  which discarded the summary line and masked the real exit code behind
1983-  tail's; **adjudicated Sol's blocker to L1 by reading the primary
1984-  source** rather than accepting the delivered severity; chose **full
--
1990-  dominance predicate reproduces both prior inline gates for absolute
1991-  and comparative **before either reviewer reported**.
1992-
1993:### Lead errors (recorded plainly)
1994-
1995-1. **The lost quiet window — the most expensive process error of the
1996-   campaign.** The lead launched the Sol clock diagnosis with
--
2014-   (`status: blocked, completion: none`) revealed it.
2015-
2016-**Generalization adopted this session (from errors 5 and the `tail`
2017:catch above): EXIT STATUS IS NOT EVIDENCE OF WORK DONE.** Twice in one
2018-session an exit code masked a non-result — a wrapper returning 0 over a
2019-blocked, read-only Sol session, and a test suite whose summary and exit
2020-status were both swallowed by `tail`. The evidence of work done is the
--
2053-  `runs_window_c_20260726_bound/`).
2054-- **Window D**: **not started** (`runs_window_d_20260726*` are empty).
2055-
2056:### Rough spend (estimates, not billing truth)
2057-
2058-Four delegated calls carry figures: the Opus 5 contract lens ~164k
2059-tokens / 50 tool uses / ~11 min; the Fable adjudication 21k tokens /
--
2115-
2116----
2117-
2118:## C-039 addendum: the FIX-6..9 gauntlet, three cold gates, and the 7B floor window (2026-07-29/30)
2119-
2120:Continuation of the C-039 index row above, covering the arc that carried
2121-`impl/mint-tool` from `f63a334` to `969a4d6` plus mint #1 and the
2122-`window_7bfloor_20260729` collection. Rulings from this arc are D-083..D-088 (D-088 in the same-day close-out);
2123-the session ledger is the magistrate's own record. Topology: **magistrate**
2124-(Fable, Ed's direct) adjudicating and operating the window solo,
2125-**lieutenant** (Opus 5) directing the Sol pipelines and assembling packets,
2126:**Sol** implementing and auditing, plus the rule-11 **cold gate** (fresh
2127:Fable instance + Opus contract-lens refuter).
2128-
2129-### Layers run
2130-
2131-| Layer | Instances | Shape |
2132-|---|---|---|
2133-| Sol implementation (enforced `WRITE_SCOPE`) | 4 | FIX-6 `ea20a82`, FIX-7 `7f2c108`, FIX-8 `a14740d`, FIX-9 `969a4d6` |
2134:| Independent audit / delta re-audit | 3+ | FIX-6 delta audit; FIX-8 audit; FIX-9+FIX-8 delta re-audit over `f188562^..969a4d6` |
2135:| Cold gate (cold Fable + paired Opus contract-lens refuter) | 3 | F1 recorded in full (D-087); the pairing is the mechanism, not decoration |
2136-| Magistrate bench verification | continuous | primary-text reads, bit-exact floor recomputation, QA-1 confirmation |
2137-| Modularity survey (Explore agent) | 1 | produced the STACK-ID-BIND-01 lead |
2138-
2139:### Unique catches, by layer
2140-
2141:- **FIX-9 delta re-audit — blocker QA-1, the arc's decisive catch.**
2142-  Overall verdict **FAIL** (Q1 FAIL, Q2 FAIL, Q3 PASS-WITH-CONCERN, Q4/Q5/Q6
2143-  PASS). QA-1: *"a partial `physical_members` list can launder a
2144-  within-member duplicate into one candidate."* A member declaring
--
2156-  supersession validator/reader with the cooldown join — the FIX-9
2157-  regressions stub the reader, which is adequate for join/matcher behavior
2158-  and **insufficient as custody-path closure**.
2159:- **FIX-9 delta re-audit — independent corroboration of the mint.** Q6
2160-  verified the artifact is valid JSON, that its cell and transport-group
2161-  values agree exactly, and that they round to the W6 pins **3.592138**,
2162-  **7.377086**, **7.377086**, with the external statement carrying the same
2163-  formula, roles, source, and no-double-count rule. Independent of the
2164-  magistrate's own bit-exact recomputation (D-084).
2165:- **Cold gate F1 — caught a defect in the magistrate's own packet.** The
2166-  packet asserted `__init__.py` was in no granted `WRITE_SCOPE`; `f63a334`
2167-  (FIX-5) had touched it and introduced the two-site surplus policy, making
2168-  F1 the un-reverted half. The cold layer's value here was **against the
2169-  magistrate**, which is precisely the disposition rule 11 exists to check.
2170:- **Cold gate F1 — C2, the phase-order verification.** The cold instance
2171-  verified from code that `_validate_output_separation` (`__init__.py:85`,
2172-  called at `:1206`) runs **before** inputs load, so the filtered mapping
2173-  does not exist at that point — converting "just filter it" into a
2174-  design-bearing choice and forcing it up to the magistrate rather than
2175-  leaving it to the implementer.
2176:- **Paired Opus contract-lens refuter — narrowed the finding and supplied
2177-  the adopted design.** F1 is **narrower than packeted** (refusal requires a
2178-  surplus entry AND (symlink OR output-containment); no soundness exposure
2179:  either way), and the refuter's **M3 — filter in place, preserve call
2180-  order** beat the magistrate's own two-phase reorder proposal, which was
2181-  **withdrawn**. M2's Opus-verified closed consumer list became a verified
2182:  precondition. Second recorded instance this arc of a paired refuter
2183-  out-designing the adjudicator.
2184-- **Modularity survey (Explore agent) — STACK-ID-BIND-01.** Flagged that
2185-  `analysis_engine/inputs.py:453` reads `artifact.get("sha256")` while
--
2194-  (D-083). B1 (device.boundary placeholders) was refuted; the referral
2195-  question — whether the two citations address different objects — was
2196-  answered YES from the clauses' own words.
2197:- **Layer that produced nothing:** the B4 pending-refuter harvest closed
2198-  **empty**. `ref/B4_sol.status` still read RUNNING from the pre-restart
2199-  harness, `ref/B4_sol.md` was never written, and the background job had died
2200-  with the old harness. Pre-assessed superseded / corroboration-only, so the
--
2213-excursion — the operator log records only an hourly-snapshot *hypothesis*
2214-for it) that the admission gates caught and that the protocol recovered from per its own written
2215-playbook — the first arc in which the recovery path was exercised rather
2216:than theorised. The **third-failure-closes** rule was ratified as cold-gate
2217-precedent during this operation (D-087).
2218-
2219-### Process observations
--
2222-  same-signature trigger before FIX-8 ran; the arc did not need to fire it
2223-  for that signature. FIX-9 is a *different* defect at a different hop, not
2224-  round three on the same one.
2225:- **The cold-gate mechanism earned its cost this arc**: three exercises, one
2226-  packet correction against the magistrate, one design substitution adopted
2227-  over the magistrate's proposal, one code-verified precondition. Retain.
2228-- **Open at the addendum's writing:** QA-1 is an unclosed blocker on
--
2234-The "open at the addendum's writing" state above resolved as follows. FIX-10
2235-(Sol high, magistrate bench-reviewed, `16c7af0`) closed QA-1 with
2236-declared-occurrence tallying and the real validator/reader/join fixture;
2237:its own delta re-audit (Sol xhigh) then **FAILED with two successor
2238-blockers** (QA-10A map-omission, QA-10B existing-retry laundering) — the
2239-second consecutive same-signature fix-round failure. The standing escalation
2240:trigger FIRED and was honoured: no FIX-11 was ordered; a mandatory cold gate
2241:(fresh Fable + Opus contract-lens refuter, exercise #4 of the pairing) ruled
2242-and the magistrate synthesized D-088 — join hardening moved to its own
2243-gauntlet under a ratified contract; the branch merge licensed at the audited
2244-head with the blockers registered.
2245-
2246:Layer catches this round: the **delta re-audit layer** caught both successor
2247-blockers a green 2280-test suite could not see (the fixtures were all
2248:hardcoded `invoked`); the **refuter layer** caught that FIX-10 was conformant
2249-with ruling R2 and the *ruling* was the QA-10B defect (a finding against the
2250-magistrate, on the record in D-088 cl.6), plus the declaration-order
2251:discriminator the cold instance's contract had missed; the **cold-gate
2252-layer** caught the structural cause (the missing existing-outcome bit) that
2253-both fix-round formulations had danced around, and the QA-10A escape path
2254-through `floor_extraction`'s map-iteration completeness. Three independent
2255:corpus scans (magistrate, cold instance, refuter) each verified both blocker
2256-shapes absent from all claim-bearing evidence.
2257-
2258----
2259-
2260-## C-039 addendum II: two escalation consults — the cooldown-join design consult and the contrast-window recovery (2026-07-30/31)
2261-
2262:Second continuation of the C-039 index row. Both entries here are **consults
2263-convened because an escalation trigger fired**, not council rounds convened by
2264-ritual — one on a code defect class, one live inside a measurement window. The
2265-rulings are D-089 (join) and the window's own §10 continuation record.
--
2270-checked against emissions rather than declarations, so a partial supersession
2271-launders a declared-but-malformed occurrence) and B2 (filtered sibling
2272-manifests never contribute declarations) — the **third consecutive round
2273:leaving a residual of the same signature**. Per hard rule 11 the next spend was
2274-a **design consult, not a fix round**; the merge train was held pending its
2275-disposition.
2276-
--
2278-codex-adjudicated with lead replays, question scoped to *where
2279-declaration-completeness is enforced* (the ONE home).
2280-
2281:**Unique catches:**
2282-
2283-- **The consult reframed the defect class out of existence rather than
2284-  patching its third instance.** D5-J moves the matcher contract
--
2293-  near-unreachable in any case; the cost of refusing is the standard
2294-  repair-or-re-collect path), leaving **exactly two accepting shapes**. A
2295-  consult that hands its adjudicator the one cell it should not decide alone
2296:  is the behaviour the pre-decision-consult rule is buying.
2297-- **Interim-merge answer NO.** The lead's own preference was a conservative
2298-  interim guard (D1) that would license the merge now; the consult established
2299-  D1 cannot cover B2, so the structural fix lands pre-merge. Second recorded
--
2304-inputs. Implementation is FIX-11 in name, **structural in kind and
2305-consult-sanctioned**, queued behind the metrology campaign authoring in the
2306-same worktree. [RESOLVED 2026-07-31: implemented first (the authoring Sol
2307:session had died), merged via PR #89 under the D-093 cold-gate synthesis;
2308-metrology authoring relaunched after the merge on `impl/metrology-campaigns`.]
2309-
2310-### (ii) Contrast-window recovery consult (2026-07-31, live in-window)
--
2314-second after a relaunch premised on a **misattributed** cause — the operator
2315-verified Time Machine was clear but did not verify overall CPU quiet, and the
2316-true cause (an XProtect Remediator sweep) was still running. The standing
2317:same-signature trigger fired; per rule 11 the next spend was a consult, not a
2318-third blind relaunch.
2319-
2320-**Layer:** bounded Sol xhigh consult, thread `019fb69a-7692`, convened by the
2321-solo window operator between stages.
2322-
2323:**Unique catches:**
2324-
2325-- **The one-invocation supersession contract.** The consult established that
2326-  the supersession recorder must be run **exactly once, post-window**, naming
--
2366-signature matched window A's post-cal attempt-1 failure from the prior
2367-night. Three same-signature calibration failures across two windows is
2368-exactly the standing escalation trigger's shape; per rule 11 the next
2369:spend was a consult, not a third blind launch.
2370-
2371-**Layer:** bounded Sol xhigh consult, read-only, one round, convened by
2372-the solo window operator between launches (~01:00–01:30 PT). Full memo:
2373-session scratchpad `693609a9…/scratchpad/consult_anchor_v2.md`; findings
2374-ratified into D-099.
2375-
2376:**Unique catches:**
2377-
2378-- **The anchor is knife-edge by construction, and the lead's mechanism
2379-  was wrong.** The operator's working theory was cadence drift in the
--
2413-the consult's unique value is causal discipline under time pressure —
2414-separating "what we can prove" from "what we are tempted to conclude"
2415-before the next launch is committed.
2416:## C-040: The commit-3 gauntlet — five fix rounds, two cold gates, and what each layer uniquely caught (2026-08-01/02)
2417-
2418-**Shape.** Composed commit (Sol xhigh, ratified design) → independent
2419-delta audit → fix rounds each followed by a FRESH-thread re-audit →
2420:rule-11 cold gates when triggers fired (twice) → [outcome line filled at
2421-close]. All delegated; magistrate gates: suite + mapping-hash pins at
2422-every head, bench verification of every load-bearing audit claim before
2423-acting.
2424-
2425:**Per-layer unique catches (zero dead layers this arc):**
2426-- Implementer self-verification: caught nothing the auditors later
2427-  confirmed as remaining — necessary but NEVER sufficient, again.
2428-- Audit 1: crash-strand ordering, v1-pinned verdict verifier (a DESIGN
2429-  scope omission it attributed as implementation), path normalization.
2430-- Re-audit 1 (fresh): proved fix-1's heal unreachable-shaped and the
2431-  same-signature persistence that fired the trigger.
2432:- COLD GATE 1 — cold instance: THE ROOT CAUSE (the design's
2433-  attest-after-publish clause guarantees the crash window; both prior
2434:  rounds were downstream patches). Refuter: the design's TWO
2435-  contradictory acceptance clauses; the pointwise-vs-enumerative
2436-  aggregation distinction that OVERTURNED the cold instance's B2 order
2437-  (magistrate overruled with dissent, bench-verified); the torn-log-line
--
2442-  breadth, test fidelity).
2443-- Re-audit 3: unbound lock token; enumeration-shaped tail (the pattern
2444-  recurrence that fired the second gate).
2445:- COLD GATE 2 (convergent): both instances independently probed
2446-  CPython's json taxonomy and rejected BOTH magistrate candidates.
2447:  Refuter uniquely: the whitespace-preservation hole (json.loads
2448-  tolerates trailing whitespace → permanent acceptance of
2449-  writer-impossible bytes) that had survived FOUR prior reviews; the
2450-  packet's miscited B3/NUL precedent. Cold instance uniquely: the
--
2458-1. Fix rounds introduce defects — now proven FIVE consecutive times on
2459-   one commit; the fresh-thread re-audit after EVERY round is
2460-   non-negotiable doctrine, permanently.
2461:2. The refuter layer's value concentrates exactly where instances agree
2462-   too readily: both its overturning arguments (B2 aggregation; the
2463-   whitespace hole) came with runnable probes, not rhetoric. Keep
2464:   requiring probes in refuter briefs.
2465-3. Formulation-vs-implementation trigger parsing is a loophole risk:
2466-   the D-104 disposition note's pattern (one explicit fidelity round,
2467-   then ANY blocker → gate + descope, no further parsing) is the
--
2469-4. Directing-subagent stalls (4×) and the MCP 1800 s timeout: audited
2470-   CLI route for >30 min Sol rounds; harvest-from-disk + process
2471-   watchdogs as standing practice (memory recorded).
2472:5. Magistrate candidate formulations in cold-gate packets get REJECTED
2473-   when drafted at the bench under fatigue (both round-4 candidates) —
2474-   the gate caught both; drafting candidates is still net-positive
2475-   (they focus the ruling) but they must be labelled candidates, never
2476-   presumptive.
2477-
2478:**COLD GATE 3 (disposition, 2026-08-02) addendum:**
2479-- Round 5 closed the lock mechanism entirely (all identity attacks
2480-  incl. field-copied clones) but left two recognizer-exactness
2481-  blockers; the binding commitment fired as written — no round 6.
2482-- Cold instance: Option A on the merits with verbatim fences + complete
2483-  closure procedures; its own wider absence scan (40 files vs the
2484-  packet's 33 — depth-1 glob error caught); demanded the third
2485:  independent scan and made lead live verification an explicit merge
2486-  condition rather than trusting the packet's uncited green claim.
2487:- Refuter (the arc's strongest document): did NOT oppose landing;
2488-  replaced the fences — the preserve-then-truncate custody sidecar
2489-  (classifier errors can no longer destroy evidence, decoupling
2490-  exactness from custody), the 2-line writer-side ASCII key assertion
--
2498-- Synthesis D-105: land via custody micro-commit + narrow audit;
2499-  registration as a NEW ruling; exactness struck for a documented
2500-  decidable superset; D-104 cl.2 amended.
2501:- Layer scorecard update: the refuter layer has now overturned or
2502-  materially amended the magistrate/cold-instance position at ALL THREE
2503-  gates — it is the single highest-unique-catch layer of the project
2504-  and its probe-required brief format is ratified practice.
--
2511-standing conditions and D-093 scans lifted per their row contracts;
2512-residual exactness blockers registered non-downgradable in
2513-C3-RECOGNIZER-EXACT-01 under D-105's compensating controls (custody
2514:sidecar; writer-side key assertion). Total spend: ~6 Sol implementation
2515:sessions, 6 independent audits, 3 cold-gate pairs, across ~20 hours of
2516-the Ed-authorized runway — the most heavily reviewed change in the
2517-project's history, protecting the machinery every future claim
2518-consumes.
2519-
2520:## C-040 addendum: the b-ii cold gate (D-106), the merge-fallback landings, and the codex envelope bug (2026-08-02/03)
2521-
2522-**Shape.** The runway's second half ran both repair branches through
2523-brief-repair rounds to decisive re-audits: MANIFEST-CONTRAST v3 came
2524-back CLEAN (zero findings) and merged as PR #95; MET-DANGLER's decisive
2525-re-audit left ONE blocker (B3-R1), the disposition note's binding
2526-commitment fired as written — no third formulation round — and the
2527:question went to the runway's FOURTH cold gate (cold Fable + Opus
2528:contract refuter), synthesized as **D-106 Variant D**. Full packet and
2529-re-audit custody: `.desk/coldgate_d100_bii/`.
2530-
2531:**Per-layer unique catches (no dead layers):**
2532-- Decisive re-audit (Sol xhigh, fresh thread): B3-R1 itself — after two
2533-  formulation rounds, telemetry and nested content remained unbound to
2534-  the admission-only event account (earlier-capture substitution
--
2537-  the parent by code inspection, under a code-inspection-only ruling.
2538-- Cold instance: Option A + window-B YES on the compensating-control
2539-  theory; its own stated strongest counterargument (doctrinal fences
2540:  decay) converged with the refuter's B-1 — recorded as dissent when
2541-  overruled.
2542:- Refuter (Opus, contract lens): the gate's decisive layer for the
2543-  FOURTH consecutive time, all showings bench-verified — the recorded
2544-  manual verification contains ZERO bundle digests, so Option A's fence
2545-  binds by path against a content-substitution defect; the packet's
--
2555-  registered.
2556-- Magistrate: Variant D synthesis; two packet-hygiene failures recorded
2557-  against itself (the Option C runway line; the selective quotation);
2558:  cold-gate packet authorship moved to MECHANICAL assembly permanently.
2559-
2560-**The merge-fallback pattern (twice, ruled):** GitHub could not build or
2561:schedule merge-ref CI for PR #94 (pull_request runs never scheduled;
2562-close/reopen tried) or PR #95. Ruled fallback, both times: satisfy
2563-D-072's substance far past precedent (three independent audits + cold
2564-gate + lead full suite at the audited head + hash-identical mapping
2565-pins; for #95, the composed-tree full suite as the lead integration
2566:gate), merge, and treat the push-to-main verdict CI as the verdict with
2567-immediate revert on red. Both verdict runs came back green.
2568-
2569-**Site failure domain (D-101 addenda I+II):** the D-106 decision-log
--
2592-runs; D100-BII-BINDING-01 minted (P1) carrying D-106 clause 3's four
2593-parts; window B re-evaluation hard-blocked on it; its focused
2594-independent audit launched 2026-08-02 evening (successor session) with
2595:the repaired codex path. Layer scorecard: the probe-required refuter
2596-brief format remains the project's highest-unique-catch instrument —
2597-four gates, four material amendments or overrulings.
2598-
2599:## C-041: The D100-BII nested-closure arc — two more cold gates, a third-failure STOP, and the CAL-BRACKET consult (2026-08-03, desk session in Ed's absence)
2600-
2601-**Shape.** One desk session ran the two open repair branches
2602-(D100-BII-BINDING-01, CAL-BRACKET-D079-01) and the MINT-GENERALIZE
2603:tooling to their conclusions, plus two cold gates on the b-ii
2604-nested-content closure. All delegated; magistrate gates: lead full-suite
2605-+ live bench probes at every disposition. Roles: Fable magistrate;
2606:Sol xhigh execution/audit/consult; cold Fable instances + Opus refuter
2607-at the gates.
2608-
2609-**D100-BII arc — three formulations, two gates, STOP (full detail:
2610-`.desk/coldgate_d100_bii/`).** The nested-content closure (D-106 clause
2611-3(c)) failed three structural formulations:
2612-- Formulation 1 (position-enumeration) + formulation 2 (key-denylist):
2613:  cold GATE 2 → **D-107**, adopting the refuter's C-A′ producer-derived
2614-  admission grammar with per-leaf value domains; scope expanded to the
2615-  inventory grammar + the 769/769 false-refusal repairs; row acceptance
2616-  amended with an over-refusal gate (license 3/3 real subjects). The
2617:  refuter's fifth consecutive material amendment: it proved the license
2618-  tool refused all three real subjects at the inventory gate at every
2619-  head, that fix-1 over-refused 769/769, and that four value channels
2620-  stayed open.
2621-- Formulation 3 (open-superset leaves): fix-2 implemented C-A′ but left
2622-  free-text `node_cleanup.error/.path`, the argv superset, and numeric
2623:  leaves open — bench-confirmed workload text licenses. Cold GATE 3 (two
2624:  cold Fable instances converged on L-A surface-refusal; Opus refuter
2625:  DECISIVE): the refuter proved (a) the packet censused the wrong
2626-  population (telemetry.command 0/26 on the license surface, and L-A's
2627-  natural implementation false-refuses 772/772 via a second .command[]
2628-  path), (b) four MORE open carriers, (c) **structurally**, the grammar
--
2641-  clause is exactly the sunk-cost pattern rule 11 exists to halt.
2642-  Nothing committed; fix-2 diff held untrusted; window B stays blocked.
2643-
2644:**Per-layer scorecard (this arc):** the Opus refuter layer amended or
2645-overturned the disposition at BOTH gates (2 and 3) — now the sole
2646-highest-unique-catch layer across SIX consecutive gates. Cold Fable
2647-instances: converged correctly on shape both times, but neither reached
2648-the structural cardinality/capacity finding — the cross-model pairing
2649-earned its keep again (a fresh Fable shares the magistrate's own
2650:dispositions). Packet hygiene: the refuter recorded FOUR findings against
2651-the magistrate's gate-3 packet (selective clause-7 quotation omitting the
2652-half that decided the gate; flags not quoted in full incl. the blocking
2653-anti-round-3 disposition; a laundered "769/769 admit" number; wrong-
--
2658-population.
2659-
2660-**CAL-BRACKET arc — consult over blind round three.** Impl + fix-round-1
2661:(first-audit blockers cleanly closed) → delta re-audit FAIL, 3 freshness
2662-blockers, estimator-digest a REPEAT signature. Per the escalation trigger
2663:the next spend was a read-only Sol xhigh DESIGN CONSULT, not a fix round.
2664-It resolved each against D-102: F1 (freshness=6-field epoch) determined;
2665-F2 (4-module estimator digest set) magistrate-ratified from the
2666-b_fiducial_s dependency graph; **F3 (cross-root trigger observability)
--
2670-F3 (it controls the artifact schema). Detail: `.desk/calbracket_d079/`.
2671-
2672-**MINT-GENERALIZE-01 — landed.** Full gauntlet (impl → audit → fix →
2673:delta clean → bench fix → lead gates → PR #96 green CI) merged under
2674-D-072; live 7B mint stays lead-reserved. The clean case of the session.
2675-
2676-**Process finding for the skills.** Two claim-machinery closures this
--
2692-explicit deferral to the joint position → D-108 + D-109. Full record:
2693-`docs/process_traces/2026-08-03-d111-backfill/debate-d108-d109/` (tracked).
2694-
2695:Unique catches, by layer:
2696-- **Sol round 1 (packet audit):** (1) the D-108 packet's "three
2697-  subjects manually verified" overstated the durable record — full
2698-  b-ii facts exist for the two r08 attempts only; (2) the packet's
--
2712-  A-min-with-reservation, withdrawn on the record.
2713-- **Convergence quality:** two Sol catches survived verification, one
2714-  magistrate counter died to code, one Sol recommendation flipped on
2715:  supplied context. Both directions of the bridge earned their spend;
2716-  the consult-before-ruling shape (rule 2 amended default) validated
2717-  again on a decision-level packet.
2718-
--
2734-independent adversarial audits then converged clean. Outcome: PR #86 merged as
2735-`7b12f20`; replayed a9 (7 members) and a10 (37 members) both passed
2736-consumption with every member widened and point estimates unchanged. The lead
2737:gate recorded 2164 passed / 21 skipped at the rebased head, with all five CI
2738-checks green.
2739-
2740-## C-047: The 16h runway — two gauntlets, the winB STOP gate, the concurrent-sweep interception (2026-08-03)
--
2745-the two-week soundness sweep mid-runway (Ed-initiated concurrent-audit
2746-pattern — validated, memorized, D080-TRIGGER-01 queued).
2747-
2748:Unique catches by layer: Sol audits — D-108 F1 (retirement
2749:over-drop), D-109 B1/B2 + four weak fences; Opus contract refuter —
2750-expired NEG-8 bound, cascade-spelling falsification, F7 barred-cell
2751-scope question, falsify-by-removal sole-cause proof; cold Fable —
2752-stage-1-clean control-flow proof, spelling-collision (two producers),
2753-masking-latency explanation; concurrent sweep — RT-1 (intercepted the
2754-in-flight 7B-mint license neither in-session consultant could see);
2755:lead bench — two fix commits, clause-(d) re-record, byte-identical
2756:pinned replay, exit-status-masking recurrence self-caught. Fix rounds
2757-introduced defects twice more (data #11, #12). Both gauntlets held;
2758-the deviation escape and rule-11 gates fired as designed; the night's
2759-one claim-surface outcome is HONEST SHRINKAGE (CLAIMS_STATUS §1 =
2760-NONE under D-110) plus a proven-honest toolchain (byte-identical
2761-replay).
2762-
2763:## C-048: Integration-collision resolution — consult-shaped amendment, delta re-audit catches a live guard bypass (2026-08-04)
2764-
2765-Session: successor magistrate, T3-drive era; the first decision handed
2766-off by C-047's close. Full record:
--
2768-(FINDING + RESOLUTION + both Sol reports) and the consult directory
2769-beside it; policy: D-109 addendum II.
2770-
2771:Shape: bounded pre-decision Sol HIGH consult (rule 2 amended; Ed's
2772-effort cap held — no xhigh anywhere this arc) → Sol HIGH enforced-scope
2773:implementation → lead bench diff-read + full-suite replay ON THE
2774:INTEGRATION TREE (2487 OK, exit-0 unpiped) → fresh Sol HIGH delta
2775-re-audit → bench hardening from the auditor's specified fix shape →
2776:merge-ref CI green. Merge itself: harness classifier denies agent
2777-`gh pr merge`; Ed names merges (standing pattern, reconfirmed).
2778-
2779:Unique catches by layer: PRE-DECISION CONSULT — the byte-identity
2780-oracle correction (historical-digest replay would have CONTRADICTED
2781-D-110; integration-tree core-vs-wrapper parity adopted instead), the
2782-review-pinned rename, the snapshot-identity regression spec. DELTA
2783-RE-AUDIT — the repr-'None' default spoof PROVEN LIVE against the
2784-rendered-signature pin (guard passed while the core's is-None load
2785-path was defeated), plus the remerge-tree fidelity proof and the
2786:loader-mutation kill of the new regression. LEAD BENCH — the piped
2787:exit-status recurrence self-caught AGAIN (third occurrence; the unpiped
2788:re-run is now reflex, the habit clearly is not), stale RUN_STATE
2789-claims (char captures "collected" that never ran; F1's byte-frozen
2790:framing in active restart text). CI — remains the only layer that
2791-structurally sees the merge ref before merge.
2792-
2793-Instrumentation note: two HIGH-effort Sol instruments again produced
2794:blocker-grade unique catches (consult F1, audit F2) — Ed's cap shows
2795-no quality decline through this arc. The delta-re-audit rule (every
2796-fix round) paid for itself on a 127-line mostly-test amendment.
2797-
--
2802-D-113 ruled (c), overnight issuance pre-authorized conditional on the
2803-gate). Full records: `docs/process_traces/2026-08-06-d079-issuance-coldgate/`,
2804-`docs/process_traces/2026-08-06-d110-remint-fork/` (DIAGNOSIS, consult
2805:prompt+response, SYNTHESIS), RUN_STATE checkpoint blocks of 2026-08-06
2806-(morning + afternoon + late), plus the per-arc consult traces of
2807-2026-08-05 in `docs/process_traces/`. This entry is the owed council
2808-record assembled by the 2026-08-07 successor from those artifacts.
--
2813-2 — CGV F3 absolute-path-bypass (consult-adopted restructure replacing
2814-the denylist approach) and QG census observation→absence class (Option
2815-C redesign, magistrate stop-condition set); (iii) fix rounds each
2816:followed by xhigh delta re-audits; (iv) the D-079 issuance rule-11 cold
2817-gate — SPLIT verdict, fresh-Fable PROCEED vs Sol-xhigh contract-lens
2818-HOLD — magistrate UPHELD the HOLD; (v) issuance reframed from "an edit"
2819-to a design-bearing consumer implementation, run through the full
2820-gauntlet (PR #108 consumer, PR #109 execution + ledger genesis import +
2821:5-file test reconciliation; two cold gates, adversarial audit + 3 delta
2822-rounds, exact-bytes dual cold review); (vi) D-116 issued, PR #109
2823-merged on green under D-072 at gate-reviewed head `d85b4f9`; (vii) the
2824-FIRST consumption attempt against the issued regime → structural
2825:finding → Sol xhigh pre-decision fork consult (run
2826-`20260806T165843Z-10884`) → magistrate synthesis.
2827-
2828:### Unique catches, by layer
2829-
2830:- **Rule-11 cold gate (the flagship):** the issuance HOLD caught that
2831-  the packet was underscoped — F1: `calibration_bracketing.py` had NO
2832-  consumer path for an issued acceptance artifact (a JSON flip would
2833-  have made it unloadable in production); F2: `derivation_sha256`
--
2836-  write paired with a production-refused artifact was prevented. The
2837-  split verdict was synthesized by the magistrate (rule 9), not
2838-  majority-voted.
2839:- **xhigh delta re-audits (fix rounds introduce defects — proven
2840-  again, twice):** QG F1 — idempotent init retry reporting success with
2841-  unresolved directory-fsync durability (introduced by fix round 1);
2842-  CGV B1 — malformed digest arg serialized verbatim into REFUSE
2843-  receipts (live-proved) and B2 — a non-CommonMark phantom fence hiding
2844-  real duplicate headings from the pin check.
2845:- **Oversight/prune lens (cgv-audit-B):** PASS receipt did not bind the
2846-  judge to the validated bytes (post-validation exhibit substitution),
2847-  plus the prune recommendation that reframed F3's whole subsystem —
2848-  the finding that triggered the CGV consult.
--
2856-  pairs physically exist under the drift screen (the objection is
2857-  provenance completeness, not causality); recommended Option 2 (three
2858-  compact prospective windows) over finite-allowlist historical
2859:  candidacy (Option 1, preserved cold-gated); flagged the D-113
2860-  dependency rewire; supplied the unblocked-regardless desk queue.
2861-
2862-### Dispositions and open state at close
--
2865-#109; PR #109 merged (`c537386`). Magistrate + consult CONCUR on
2866-Option 2; **Ed had NOT ruled at the machine-move stop** — his ruling,
2867-the prefill-contrast shape ack, and three-nights scheduling were the
2868:owed items handed to the successor (RUN_STATE checkpoint block).
2869-Wrapper gotcha re-recorded: codex-run-v3 takes the prompt as a literal
2870-string, never a file path (one consult killed + relaunched cleanly).

exec
/bin/zsh -lc "sed -n '466,665p' docs/council_log.md; sed -n '666,925p' docs/council_log.md" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
## C-006 (session trace + meta-review, 2026-07-07): six-stream parallel batch, integration review, process meta-review

Streams: A uncertainty/D-014 (in flight) · B campaign automation (merged,
PR #3) · C mock-hardening/P2-008 (in flight) · D rich-telemetry/P2-009
(merged, PR #4) · E kv-size helper (merged, PR #2) · F repo test-audit
(in flight). Plus: ideation council (DL-1) and a post-merge Codex
integration review over merged main.

### Shape (orchestration decisions)

- **Decomposition — 5 implementation streams + 1 audit stream, parallel:**
  the queue held independent, file-disjoint tasks; worktree-per-stream
  isolation makes collision structurally impossible (checked against
  expected `git diff --stat` footprints before fan-out). Sequential would
  have serialized ~15-min Codex rounds behind each other for no safety gain.
- **Model assignment:** Fable for stream orchestrators — each stream needs a
  judgment GATE (final-diff review, finding triage, commit decision), not
  volume analysis. Codex 5.5-high for all implementation/review/test volume —
  near-limitless quota makes redundant fresh-eyes passes free, and fresh
  Codex instances carry no thread state, so a fresh instance is a genuinely
  independent reviewer even of Codex's own code. (Gen-1 launch violated
  this by accident — see I-2.)
- **Review tier per stream (scaled by cost-of-being-wrong):**
  - A, C, D — measurement semantics; a defect poisons the scientific
    validity of every future number → FULL: Codex design round, 3-lens
    counterreview, test amplification, writer≠reviewer test review, lead
    live-verify.
  - B — operator-facing campaign script; failure wastes a session, not the
    dataset → standard: counterreview + amplification + fresh test review +
    orchestrator live-verify against the real CLI (which is what caught K-4).
  - E — pure calculator, no runtime surface → lighter: counterreview lenses
    + orchestrator diff gate (which caught K-1..K-3 — the light tier still
    carried its weight).
  - F — audit-only; findings reported, never fixed in-stream (other streams
    own the code).
- **Ideation council: 4 lenses + devil's advocate** — breadth beats depth
  for agenda-setting; divergence is the point (council skill, shape B).
- **Post-merge integration review added** because per-stream review
  structurally cannot see cross-stream interactions. Vindicated same
  session: it found 2 real interaction defects (K-9, K-10).

### Catches (differential attribution)

| id | what | sev | caught by | missed by | enabler | counterfactual |
|---|---|---|---|---|---|---|
| K-1 | silent head_dim floor in KV-size calc | med | fresh-eyes Codex counterreview lens (E) | Codex implementer AND Fable orchestrator review | writer≠reviewer: fresh instance, no thread state | wrong KV payload numbers feed Phase-3 transfer planning |
| K-2 | text_config precedence ignored (nested config) | med | same lens (E) | same both | same | wrong KV numbers for exactly the model class we benchmark (MoE/nested) |
| K-3 | bare-ValueError catch-tuple, over-broad blast radius | should-fix | Fable orchestrator diff gate (E) | Codex implementer | Fable-final-gate doctrine (thin ≠ rubber stamp) | unrelated errors silently swallowed as parse failures |
| K-4 | campaign resume checks a path the real CLI never creates | blocker | orchestrator LIVE-verify vs real CLI (B) | implementer + its GREEN tests (the stub encoded the same wrong contract) | live-verify doctrine: tests green never sufficient | first real overnight campaign silently fails to resume |
| K-5 | campaign robustness ×5: lock, torn log, sanitization, half-written summary, config-error abort | should-fix ×5 | Codex counterreview lenses (B) | implementer | mandatory counterreview after every implementation | operator-facing failures mid-campaign, partial evidence on disk |
| K-6 | rich-write failure aborted stop_sampling AFTER raw preservation | blocker | Codex counterreview (D) | implementer | mandatory counterreview | a parser bug destroys the very run it instruments — violates D-002's re-reduce promise |
| K-7 | runtime-clock anchoring broke regenerability-from-raw | blocker-class | test-AMPLIFICATION round (D) | implementer AND counterreview | amplification WRITES adversarial tests, doesn't just read | bundles not re-derivable from raw/ — core auditability promise broken |
| K-8 | lead's own verification run contaminated (agent-fleet display compositing held GPU ~75% busy) | measurement-validity | the idle-quality gate ITSELF (D) — its first true positive | the LEAD's prediction | building quality gates into the instrument | contaminated idle baseline blessed into the corpus; instrument outperformed operator |
| K-9 | stale-config glob landmine across streams | should-fix | post-merge Codex integration review | every per-stream review (structurally blind to it) | integration-review step exists precisely for this class | first mixed-stream run trips on stale configs |
| K-10 | unconditional per-rep env capture (cross-stream interaction) | should-fix | same | same | same | per-rep overhead inside measured runs |

### Deliberations (design-bearing disagreements only)

- **DL-1 (ideation council):** recorded in full in the C-005 entry above
  (12 adjudications, each position -> attack -> reasoning -> outcome ->
  dissent; per-lens unique contributions; killed/deferred list). Pointer,
  not copy, per one-fact-one-home.
- **DL-2 (stream D, idle-gate shape):** counterreview lens attacked the
  implemented min-based suspect rule as too twitchy — fixture margin to
  false-positive was 0.047 on `gpu_idle_ratio_min`; a single scheduler blip
  would flag a clean idle window. Orchestrator position: min is the honest
  detector (one busy sample = contamination). Resolution after 1 round:
  persistence rule adopted (suspect iff >=40% of idle samples below 0.80
  GPU idle_ratio OR mean GPU freq > 800 MHz) — contamination that matters
  is sustained, blips are noise; boundary tests pin both sides. Lens
  prevailed; no dissent recorded. Binds: the 0.40 threshold has no
  empirical contaminated-window corpus behind it yet (revisit flagged in
  PR #4).
- **DL-2b (stream D, artifact placement):** Codex argued rich derived
  JSONL must NOT live under `raw/` — "derived data under raw/ weakens
  raw-as-source-of-truth (D-002)"; a top-level artifact via a
  `write_derived_artifact` seam needs zero controller plumbing and keeps
  D-024. Orchestrator accepted, added the idle-window variant Codex had
  not proposed. Both prevailed in part; outcome is the committed layout.
- **DL-2c (stream A):** design amendments (plain JSON aggregate dicts with
  UncertaintyInterval internal to n>=1 paths; structured problems instead
  of exceptions) — stream still in flight; its final report carries the
  full block per the standing trace requirement.
- Streams B/E: no qualifying deliberation blocks — findings accepted on
  argument without design-bearing dissent. Zero blocks is a valid outcome.
- Merged streams B/E: no qualifying deliberation blocks known to this
  reviewer — findings were accepted on argument without design-bearing
  dissent. Zero blocks is a valid outcome.

### Interventions (lead acted from outside the agents' self-reports)

| id | failure mode | detected via | fix | folded into |
|---|---|---|---|---|
| I-1 | 2/5 gen-1 orchestrators stalled, ending turns to "await" a poll-only bridge | lead observed ended turns with idle Codex processes | prompts now MANDATE poll-in-turn or background-Bash + watcher | codex-delegation + multi-stream skills, same session |
| I-2 | all 5 gen-1 streams silently inherited Opus (session accidentally started on Opus) | lead inspected spawn config, not agent self-reports | explicit `model: "fable"` mandatory; relaunch was CHEAP — worktree diffs, bridge state, and Codex `resume --last` all survive agent death | multi-stream skill |
| I-3 | one Codex lens wedged silently ~50 min (stdin hang: `codex exec` in background Bash without `< /dev/null`) | OUTSIDE evidence only: `ps` etimes + output-file mtimes vs finished siblings (agent reported nothing) | external kill; `< /dev/null` mandatory on every `codex exec`; fleet-health-check practice born (classify long-runners from ps/mtimes, never self-reports) | codex-delegation + multi-stream skills |
| I-4 | stream A accidentally stopped by the user | SendMessage returned "no active task" while siblings returned "queued" — a reusable stopped-stream detector | relaunch on surviving worktree state | this log (diagnostic recorded) |

### Layer yield + spend (rough; spend capture starts next session)

- Fresh-eyes Codex counterreview lenses: 2 unique (K-1, K-2) + 6 robustness
  (K-5, K-6). ~free (Codex quota).
- Fable orchestrator diff gates: 1 unique (K-3). Orchestrator context.
- Orchestrator live-verify vs real CLI: 1 unique blocker (K-4).
- Lead live-verify: 0 unique catches this session — but was itself CAUGHT
  by K-8; the layer's value this session was running the instrument that
  outperformed it.
- Test amplification: 1 unique real bug (K-7) + 14 edge tests (B).
- Fresh-instance test review: 6 vacuous/tautological tests fixed (B) + 2
  mutation gaps (D). No unique code bugs — on watch as a BUG-catch layer;
  clearly earning as a TEST-quality layer.
- Integration review: 2 unique (K-9, K-10) on its first outing.
- Opus refuter tier: not used this session; 0 unique catches for 2+
  sessions → drop from default roster per the council's own rule (C-006).

### Doctrine changes (adopted this session, each folded same-session)

1. Liberal Codex — near-limitless quota → counterreview after EVERY
   implementation is the default (council + codex-delegation).
2. Test doctrine: amplification round + writer≠reviewer fresh-instance test
   review (codex-delegation).
3. Apex/volume split: Codex = volume (reading, lenses, tests, computer
   use); Fable = orchestration + final gates (codex-delegation + council).
4. Failed-test triage: Codex first, Fable after 2 Codex failures
   (codex-delegation).
5. Poll-or-watcher mandatory in orchestrator prompts (I-1) (codex-delegation
   + multi-stream).
6. Explicit `model:` on every orchestrator spawn (I-2) (multi-stream).
7. Fleet health checks from outside evidence, on landing or ~hourly (I-3)
   (multi-stream).
8. Post-merge integration review is a standing step (K-9/K-10)
   (codex-delegation).

### Meta-review C-006 verdicts adopted (same session)

- Council log was HALF-INSTRUMENTED (catch attribution prose-only, zero
  spend records => drop-a-layer unenforceable). Fix: this entry is the
  first in trace format v2 (Shape / differential Catches / Deliberations /
  Interventions / Layer-yield); v2 + threshold adopted into the council
  skill. Spend capture starts next session.
- Opus refuter/verifier tier DROPPED from the default roster: zero unique
  catches since C-001; function absorbed by fresh-instance Codex
  counterreview + Fable gates. (The council's own evidence rule, applied
  to itself.)
- Skills stack violated one-fact-one-home (doctrine restated up to 4x,
  memory file a shadow copy; adversarial-review doctrinally stale,
  pre-apex/volume) — dedup + adversarial-review update ordered same
  session; consistency-sweep scope extended to the skills themselves.
- Raw .codex-bridge logs: distill + quote into traces; archive to the
  R-016 backup area on worktree removal; never commit; prune after the
  entry lands. (This session's logs archived before cleanup.)
- operation-loop skill (single conductor-score loop over all meta
  processes,every step with skip conditions) drafted; pending lead gate.

### C-006 addendum (post-entry landings, same session)

- **Streams A and C landed** (PRs #6, #5) after the entry above was written;
  all five implementation streams + both integration fixes are now merged.
  New catch rows: **K-11** (A, stats lens): OverflowError crash on huge JSON
  ints in aggregate math — real bug, fixed with structured
  `non_finite_overflow` status. **K-12** (A, same lens): non-finite
  `Infinity` leakage into manifest JSON from extreme spreads/subnormal MAD —
  fixed (nulled + status; outlier kept with `modified_z: null`). **K-13**
  (C, orchestrator): review-lens over-strong assertion (all samples strictly
  interior) cut to the reducer's actual contract — the one genuinely flaky
  assertion removed before it could poison CI.
- **Deliberation blocks now on record** in the stream reports (quoted in
  full there; key adjudications): A's load-bearing disagreement — Codex
  refuted populating per-member `SummaryMetrics.uncertainty` ("structurally
  wrong: one interval with one mean, while D-014 needs intervals for many
  metrics"); orchestrator accepted but required each aggregate entry to BE a
  serialized `UncertaintyInterval` — hybrid resolution, both prevailed in
  part. A's orchestrator also overrode 2 test-review BLOCKERs (downgraded
  with rationale; the lens's mutation concern adopted via a
  poisoned-aggregate test) and accepted Codex's stricter
  no-auto-without-outliers reading of D-014. C's three-way design
  adjudication: (a) unconditional interior stamping won because (b)
  clock-type detection "makes mock telemetry a different adapter under
  FakeClock than under SystemClock… would preserve the blind spot that let
  this composition bug escape."
- **Intervention tallies:** I-3 (lens wedge) recurred ×5 in stream C (incl.
  amplification + test-review rounds; orchestrator substituted a
  revert-mutation check: adapter reverted to HEAD → 13/18 new tests fail —
  the strongest writer≠reviewer evidence in the session) and once in C-005 —
  all before the `< /dev/null` fix propagated; zero recurrences after. I-4
  (accidental user stop) recurred ×2 (C-006 meta-agent mid-dedup; session
  restart killing A/F mid-flight) — both recovered loss-free from on-disk
  state (worktree + bridge outputs + scratchpad lens files), confirming the
  relaunch-is-cheap property as a designed-for invariant, not luck.
- **Integration findings closed:** INT-001 (stale-config refusal,
  `a05e54d`) and INT-002 (per-experiment shared env snapshot with provenance
  fields + deterministic FakeClock skip, `8856c04`), both Codex-implemented,
  lead-gated, live-verified.
- **D-014 acceptance evidence (lead, real hardware):** n=3 real MLX
  experiment → 10 metrics aggregated, energy/output-token 99.19 ± 1.36 mJ
  (Student-t 95%, CV 0.55%), `below_headline_protocol: true` correctly
  flagged, aggregate re-derived BYTE-IDENTICALLY from bundles alone.

---

## C-007: Whole-project design/planning council + P2-013 fix design (user-directed)

- Date: 2026-07-07. Participants: Fable (lead, final judge), Codex gpt-5.5
  (7 parallel read-only lenses + 1 round-2 attack session). Shape: ideation
  council (skill shape B) — lead wrote position briefs FIRST (9 P2-013
  positions, 7 project positions), lenses argued against them, lead
  adjudicated a synthesis, a fresh Codex session attacked the synthesis,
  lead ratified with the attack's changes. Two genuine rounds of
  cross-model back-and-forth; no implementation.
- Subject: Ed asked for a project-wide council — design, architecture,
  high-level docs, planning — with Fable as final judge.

### Resolutions (what the consensus settled)

P2-013 fix design (implementation stream to follow, Codex-led):

1. B2/S5 provenance check lands in DEFAULT validation
   (`BundleReader.problems()`), not `--strict` — structural-vs-analytic is
   the D-030 boundary and byte-provenance is structural. Metadata
   object-shape (B3) checks first. All 6 corpus bundles already carry the
   field (lead-verified).
2. B1 completeness: ONE shared summary validator used by both
   `_check_summary()` and `is_complete()`; required keys per status;
   succeeded ⇒ headline energy fields present AND finite; token-derived /
   idle-subtracted metrics stay nullable. D-011 amendment note.
3. Shared finite-number primitive in a new dependency-free
   `joulewise/validation.py` (unanimous); powermetrics RICH telemetry stays
   diagnostic-only, never gates a bundle.
4. B5 duplicate rail rows: reject via one shared trace-validation path
   consumed by both `summed_curve()` and default validation; covers
   single-rail manifests. D-027 amendment.
5. B8: temp-file + same-dir rename inside the low-level write helper;
   helper cleans only its own temps; adapters never own cleanup.
6. A1 leniency: last-frame-only, ≥1 complete frame required, dropped tail
   recorded DURABLY in bundle evidence (adapter diagnostic), midstream
   failures still fail. Truncation-vs-corruption is not provable without
   framing checksums; the durable diagnostic is the honest compensation.
7. **Raw-to-trace gate (the council's biggest new catch, examiner lens):**
   strict mode today proves summary ↔ `power_trace.csv` but never that the
   CSV derives from `raw/powermetrics.plist` — D-030's "re-reduces from raw
   artifacts" wording overclaims. Adopted: powermetrics-only strict
   sub-check re-deriving the trace from the raw plist (+ anchor offset),
   IN-STREAM with P2-013 before any 2M data; D-030 wording corrected.
8. Sequencing: P2-013 (now including the raw-to-trace gate) lands BEFORE
   the P2-006 campaign. Honest rationale recorded: the capture-touching
   subset (A1/A5, B8, rank 1, R2–R5, B1 resume semantics, B2 provenance)
   gates hardware time; the rest rides along because pins are written and
   bounded. Pre-named fallback P2-013a = that subset, if a rare quiet
   window appears first.
9. Commit grouping: planning lens's 7 invariant-shaped groups adopted OVER
   the lead's priority-shaped 7. expectedFailure pins flip in the same
   commit as each fix. Post-landing target: 415 tests / 0 expected
   failures + `--strict` green over all 6 real bundles without rewriting
   them.

Project level:

10. Critical path has flipped from code to data. Instrument FEATURE work
    stops after P2-013 until 2M data exists; carveouts: evidence-integrity
    fixes never stop; cheap contract-preserving amendments that protect
    future data interpretation are in scope pre-2M.
11. Pre-2M contract amendments (new task P2-014, trimmed by the attack
    round to true blockers): (a) summary provenance (reducer/schema
    version recorded in summaries) before the corpus exists;
    (b) `phase_energy_j` pinned GROSS-ONLY in v0.1 (idle-subtracted phase
    attribution is Phase 4 analysis policy) — decided in-council, needs a
    decision-log entry when implemented; (c) composite event node identity
    = `metadata` field (per the 2N.9 flag) as a DOC alignment note only;
    (d) design note pinning BundleReader = single-node bundles, future
    CompositeBundleReader = split bundles.
12. Architect verdict accepted: BundleReader / controller lifecycle /
    strict validation / runtime-adapter capabilities / event key-set all
    BREAK for Phase 3 composites — as designed, this is Stage 3.1 work,
    not now; item 11 is the cheap protection.
13. Machine-state queue lanes adopted: QUIET-MAC / AGENT-COMPATIBLE /
    ED-EXTERNAL; sessions pick the top task compatible with their lane.
14. Two-claim-track framing adopted: auditable local measurement (harness
    + Apple-Silicon characterization) is the guaranteed capstone; split
    inference remains the validating study that upgrades it — NOT demoted
    to optional. Q4 phrased as fixed-vs-marginal workload structure (not a
    scaling law — two confounded points); Q5 narrowed on one machine to
    workload/model/quant ranking stability.
15. Detection floor confirmed UNOWNED (echoes C-003's "methodology
    centerpiece") → becomes an implementation-backed Phase 4 acceptance
    gate tied to aggregation/claims: per-target/metric floor,
    minimum-sample rule for phase attribution (~9 Hz sampler cannot
    resolve 94 ms prefill standalone), effect-size-vs-floor table,
    below-floor claims read "not resolvable" never "no difference".
16. Docs: no new authority docs. Queued maintenance: PROJECT_STATUS
    update-ledger scheme (≤2 prose update blocks), README
    prototype-status banner + mock-path-first, three named drift fixes
    (AGENT_PLAN 2G/2H/2I checkboxes; Do-Not-Do-Yet desk-spike vs
    data-collection wording; playbook gate summary), slimmer M0 intake,
    RUN_STATE history trimming.
17. Execution order (next 5): P2-013 [AGENT] → P2-014 [AGENT] → P2-006 2M
    [QUIET-MAC] → Stage 3.0.1 spike [AGENT] → P2-010 → P2-012 [AGENT].
    Ed's parallel track [ED-EXTERNAL], explicitly flagged as a real
    coordination load: calendar, device access, borrow window, wall
    meter, P0-003 backup destination — ideally one pass.

### Deliberation trace (design-bearing disagreements)

- **Lead conceded PP6 (architecture) to the architect lens.** Lead's brief
  said "no new architecture work now"; architect showed five seams break
  for Phase 3 and named three cheap amendments whose cost explodes once
  the 2M corpus exists ("data outlives code"). Lead's counter — full
  composite work still waits — survived; the amendments did too. Both
  positions are in the consensus as item 11/12.
- **Lead's commit grouping lost to the planning lens.** Lead grouped by
  priority (blockers first); planning lens re-grouped by INVARIANT
  (finite-number policy as one cross-module commit) and showed the lead's
  group G was a grab-bag. Adopted wholesale.
- **The attack round caught the synthesis's own contradiction:** section B
  declared "evidence-integrity fixes never stop" while section A left the
  raw-to-trace gate's timing open — "those cannot both stand." Lead
  ratified in-stream placement. This is the second time (after C-002) the
  reverse/attack direction caught what all forward lenses missed.
- **Q4/Q5 promotion (PP3): strategist and project-examiner converged
  independently** on the same refinement from opposite starts — strategist
  from committee-risk economics, examiner from "would read as pre-emptive
  retreat unless framed as a floor." The convergent two-track wording was
  adopted verbatim-ish. Dissent recorded: strategist warned against any
  language making split sound optional; examiner conditioned the framing
  on 2M + detection floor landing first. Both conditions kept.
- **Overridden:** examiner lens (P2-013 round) wanted CLI/report/clock
  fixes deferred out of the stream as "polish in the defense queue"; lead
  kept them in-stream (pins already written, groups isolate risk, and the
  queue item's acceptance is "all 31 pins flip"). Recorded as dissent, not
  consensus.

### Per-layer catches (instrumentation)

| layer | unique catches | notes |
|---|---|---|
| design lens (P2-013) | shared-summary-validator + shared-trace-path designs; B1 "present ≠ non-null" trap; cleanup ownership | shaped 3 consensus items |
| examiner lens (P2-013) | **raw-to-trace gap** (biggest catch); durable-evidence condition on A1; historical-corpus non-rewriting policy | major-revision verdict drove real scope change |
| planning lens | invariant-shaped commit groups; run_bundle_layout/checklist/council-log bookkeeping omissions; 7-not-6 audit test files; RUN_STATE staleness | beat the lead's grouping |
| architect lens | five seams break for Phase 3; three pre-2M contract amendments; composite-reader split note | overturned lead's PP6 |
| strategist lens | machine-state lanes ratified; 3.0.1-before-workload-buildout; "feature work stops" carveout; Ed one-pass external push | |
| project-examiner lens | detection floor confirmed unowned + concrete gate spec; phase-attribution-below-resolution objection; two-point scaling confound | supplied the "one change" (item 15) |
| docs lens | update-ledger scheme; index drift (C-005/C-006 missing — fixed this entry); three named drift items; slimmer M0 | |
| attack round (Codex, fresh) | A/B contradiction in lead's synthesis; B2 scope trim; Ed-burden flag; D-030 wording overclaim; 6 code spot-checks all confirmed | ratify-with-changes; all changes accepted |

Spend: 8 Codex read-only sessions (~free per economics doctrine); lead
context spent on briefs, adjudication, and this record. Zero-unique-catch
layers: none — every lens landed at least one consensus-shaping catch.

### Follow-ups

- Queue: P2-013 re-ranked to 1 (scope grows by raw-to-trace gate +
  bookkeeping superset), P2-014 created, lanes annotated, Do-Not-Do-Yet
  wording fix — this session.
- Decision-log entries land WITH the P2-013/P2-014 implementation (D-011,
  D-027, D-030 amendments; phase_energy_j; provenance; lanes convention).
- Docs maintenance queued as its own task (item 16), not done inline.
- PROJECT_STATUS refresh + two-track framing: with the docs task.


---

## C-008: Multi-stream session, checkpointed (2026-07-07 PM)

Session entry (format v2), kept slim because the full Shape / Catches /
Deliberations / Interventions / Spend record was preserved VERBATIM as
`docs/run_reports/2026-07-07-checkpoint-session-trace.md`, and the
product state + restart instructions live in
`docs/run_reports/2026-07-07-checkpoint-multistream-session.md`. Do not
restate; read those.

Pointer entry (per the C-009 recording rule): all product state,
process learnings, per-layer catches, and the calibration aggregate
live in the run report + its Process Trace Appendix. One
deliberation-class fact belongs here: the session's process conventions
(ledgers v2, calibration schema, decision-review doctrine) were shaped
by a Codex review that OVERTURNED two lead-designed schemas — dissents
and adjudications in the trace appendix.


---

## C-009: Meta-review of the orchestration system (SIGNED consensus)

- Date: 2026-07-07. Participants: Fable (lead), Codex gpt-5.5 (2 blind
  analysis sessions + 1 conferral session). Shape: both sides analyzed
  the process architecture and all logs BLIND to each other, then one
  conferral round; Codex SIGNED with 2 amendments + 1 gap rule, all
  accepted. This entry earns full-entry status under its own rule
  (durable doctrine + a real position reversal).
- Blind convergence (both sides independently): hybrid topology by
  stream shape; foreground bounded waits for retained orchestrators;
  heartbeat = backstop not scheduler; Codex up-stack; ledgers keep with
  ride-code-commits discipline; docs consolidation to single-writer;
  preflight gates from the session's actual failures.
- Genuine disagreement + resolution: WHERE the durable session process
  record lives. Codex's architecture lens said council log; Fable + 
  Codex's own docs-audit lens said run report (trace as appendix,
  council log reserved for deliberation). In conferral Codex CONCEDED:
  "my earlier council-log-as-process-history position was too broad
  given the duplication evidence." Adopted: run report = the session
  record; council log = index rows + genuine-deliberation entries only.
- Codex amendments (accepted): bounded waits get a STALLED-handback rule
  (never infinite loops); retired ledgers leave a branch/hash pointer.
  Gap rule (Codex): every retired working artifact leaves a discoverable
  pointer in its replacement home — path, branch, hash, promoted vs
  intentionally not promoted.
- Evidence highlights that drove the consensus: the same checkpoint fact
  written into SIX surfaces (docs audit, cited per-file); the wake gap's
  two fleet-wide stalls; the calibration ledger's design-freedom signal;
  the docs audit falsifying a claim in the lead's own run report
  (missing D-CHECKPOINT).
- USER RATIFICATION CONDITION (Ed, same day, binding): Fable is the
  APEX and final say on all high-level processes — the smartest model
  on the team; every other model's role exists to save Fable tokens,
  never because its judgment is preferred; "lead" in all topology
  tables means the Fable main loop; adjudication of any challenge to a
  Fable decision is itself Fable's. Encoded in operation-loop §3 +
  multi-stream topology preamble.
- Consensus text: run report §"Meta-review consensus"; durable homes =
  the operation-loop + multi-stream-worktrees + codex-delegation skills
  (rewritten same-session). Migration executed same-session: trace
  merged into run report, RUN_STATE slimmed to pointer shape, queue
  cells slimmed, C-008 converted to pointer style, codex-run patch task
  queued.

---

## C-010: Resume + merge session — C-009 topology first full run (2026-07-07/08)

Pointer entry: all product state, the per-layer catch/yield table, the
delegation-calibration aggregate, and restart instructions live in
`docs/run_reports/2026-07-07-resume-merge-session.md` (Process Trace
Appendix included). PRs #8/#9/#10 merged (Ed-directed, after a
3-reviewer pre-merge oversight pass with lead triage + 5.5 fixes);
PR #11 open. Deliberation-class facts for this log: (1) the lead-driven
codex-run topology ran a full session with ZERO wake stalls and zero
heartbeats — the C-009 T1 hybrid is validated on its pipeline half;
(2) two PINNED wire contracts (B-14 ssh argv, B-15 remote-root
derivation) were overturned by the lens round after unit tests had
faithfully pinned the broken shapes — fixture-first streams now always
carry the full lens tier (folded into multi-stream-worktrees);
(3) a volunteered 5.5 addition (vLLM provenance) was rejected at the
lead diff gate for hashing fabricated token IDs as realized evidence —
first clear model-defect row in the calibration ledger; the correction
(node-realized IDs via /tokenize or structured absence) is ledgered
B-44 with D-033 pressure intact; (4) K5's audit pin was adjudicated
unsatisfiable-as-authored and corrected at equal assertion strength —
the pin-correction protocol (STOP-and-report → lead ruling → sanctioned
edit) worked as designed.

Addendum (same session): PR #11 subsequently MERGED under Ed's new
standing self-merge-with-review authorization; the final fresh-eyes
pass over its post-review commit caught a real crash path + broken
checklist snippets first (fixed as B-45/B-46) — validating the
final-head rule now in operation-loop §5. All four streams landed;
main suite 546 OK.

---

## C-011: Counter-review of the independent project critique (2026-07-08)


exec
/bin/zsh -lc "sed -n '924,1216p' docs/council_log.md; sed -n '1217,1513p' docs/council_log.md; sed -n '1530,1679p' docs/council_log.md" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
## C-011: Counter-review of the independent project critique (2026-07-08)

FULL ENTRY (genuine deliberation). An independent 5.5 critique of the
entire project (docs/project_critique_review.html — goals, docs,
architecture, tests, methodology, stack; "strong instrument, not yet a
settled study") was counter-reviewed per Ed's directive: four
verification lenses checked every claim against code/docs/decision-log
ground truth with citations; the lead drafted dispositions; a bounded
5.5-high discussion round adjudicated six contested points; consensus
was reached on all six (no recorded dissent). Separately and first, a
consensus round on the new docs/site pages reached full agreement
(11 review findings + 3 new from the discussion itself, all applied).

Verification verdicts (details in the four lens out-files, summarized
in the run-report addendum): the campaign fail-closed cluster CONFIRMED
unanimously (skip-if-summary-exists, ok==exit-0, failed members
skippable — the highest-leverage finding, directly in the 2M path,
sharpened by the lenses with the reducer's config-token-denominator
fallback); the methodology cluster CONFIRMED at implementation level
while partly settled at planning level (C-007/DOC-007/D-014/D-018
already own the policies; mechanics were missing); the architecture
cluster judged directionally right but mis-timed (all queued post-2M;
RemoteNodeSession rejected per B-1's revisit clause, run-ID
randomization rejected per D-010/D-022); the docs cluster partly stale
(main pages already reconciled) but caught the flagship report's
surviving active-parameter overclaim and two stale-open Mac risks.

Contested-point outcomes: (C1) historical records stay immutable — the
flagship overclaim is superseded by a dated ADDENDUM, not amended;
(C2) the PROJECT_STATUS process section stays per Ed's explicit
showcase instruction but drops its self-congratulatory register (the
critique's compression recommendation was DECLINED in part — recorded
here as the one place the council knowingly deviated from the critique,
on the owner's standing instruction; residual tension flagged to Ed);
(C3) the claims ladder is adopted NOW as a binding contract
(docs/contracts/claims_ladder.md, D-037) because it disciplines the
imminent 2M report, with per-claim IDs deferred to Phase 4; (C4) idle
fail-closed enforcement lives at the CAMPAIGN layer with manifest-level
waivers — D-011 run semantics and strict's evidence-integrity scope are
both preserved, and waivers are never written into bundles; (C5) phase
identifiability ships pre-2M as a sample-count rule (>=3 per nonzero
interval) with the energy-floor gates arriving via the new P2-015
calibration campaign; (C6) 2M ordering is model-blocked,
workload-rotated, counterbalanced with a recorded imbalance — full
round-robin rejected for reload cost per D-014's own carve-out.

Implemented same-session on stream/critique-response (ed31d84, dbc37ed,
a42aeed): fail-closed campaign runner + verdict block + waiver schema,
counterbalanced order manifests, reducer honesty flags, claims ladder +
D-037, flagship addendum, stale-docs batch, R-002/R-003 re-scope,
P2-015/P2-016 queue items. Suite 546→555; 6/6 legacy bundles remain
strict-valid; mock e2e strict-valid.

Process note for the meta-loop: the deliberation rounds themselves had
independent yield beyond adjudication — the site round contributed three
findings its own source review missed; the critique round tightened two
designs into mechanical rules (C5's sample threshold, C6's rotation
scheme). Discussion-before-decision is earning its cost.

Addendum (2026-07-08): a second-pass reassessment was added to
`docs/project_critique_review.html` after C-011 implementation. Lead
fact-check verified 16/17 checkable claims; the one stale claim was the
Mac powermetrics/MLX risk-register wording, now annotated because
R-002/R-003 are closed-residual. The second pass updated several
first-pass passages in place and marks them in-document; the verbatim
C-011 first-pass text remains in git history at commit 6418084. A
follow-up fix pass added provenance layering annotations, hardened the
reassessment against repo evidence, and recorded this addendum-only
process footprint; the process-doc entries themselves are addendum-only.

## C-014: Workload-suite science hardening council (2026-07-08)

FULL ENTRY (genuine deliberation; position reversals recorded). Convened
on Ed's session directive: harden the science the prompt/workload suite
can answer and decide what to build next. Shape: lead independent audit
(formed before any lens output, deliberately), Codex scout packet, three
fresh Codex design lenses (statistical power/DoE, negative-space
consumer audit, adversarial confound hunt), lead triage with
dispositions, one Codex peer counterreview of the full synthesis with
design judgment explicitly invited, lead adjudication. Design docs
implemented by a pinned Codex session; lead diff gate before commit.

Convergent blockers (lead + all three lenses independently): Q4
unreachable at L3 from the 2M 4-cell grid; P2-015's absolute floor is
not the comparative MDE that gates L2/L3 claims. Unique catches by
layer: skeptic — jw_mixed category x shape confound (the C-W.1 null was
unfalsifiable as designed), silent long_short cap divergence, drift
sentinels, content-sensitivity sentinel promotion; power — the MDE
arithmetic (n=5 resolves ~1.5-1.8x CV), C5-1.1 between-model df
insufficiency, rank-gap rule, binomial energy/correct guard;
consumers — Q4-Q6 had NO Phase 4 figure/claims-index consumers, P2-010
substrate/ladder split, energy_token_j over-promotion under config
denominators; scout — phase-gross vs idle-subtracted headline mixing,
token_count_source naming drift, summary_provenance not strict-required.

Deliberated outcomes (all consensus; no dissent recorded):
(1) P2-010 splits into substrate + smoke ladder, full scored campaign
deferred — amends C-004's packaging; peer AGREE. (2) jw_mixed_v1 runs
phased with a common-shape identification stratum — supersedes C-005's
fixed-budget-full-first sequencing; peer AGREE ("spend-before-
identification"). (3) Quiet-window packing: lead leaned one window; peer
OVERTURNED to two (MDE-sized n cannot precede the floor campaign; a 4-6h
single window raises drift risk exactly while establishing a floor) —
lead adopted. POSITION REVERSAL. (4) Q4 grid: lead proposed 3x3; peer
AMENDED to 4x3 with named interpolation + extrapolation holdouts and
categorical-additive-first fitting — lead adopted. POSITION REVERSAL.
(5) analysis-plans contract adopted as a compact binding table (D-038);
peer contributed the full field schema and the pseudo-replication rule
(item windows are not independent replicates) — a gap every other layer
missed. (6) Consumer-lens implication that the next suite must include
the split matrix REJECTED: Q1-Q3 are Phase 3's by design (D-034 gate
unchanged).

Bindings: D-038 (analysis plans), D-039 (workload program v2). Queue:
P2-015/P2-006/P2-010/P2-012 amended; P2-019/P2-020/P2-021 added.

Meta-loop yield note: the invited-peer-design pattern paid again — two
lead designs overturned with strictly better ones (grid, window
packing), consistent with the 2026-07-07 calibration signal that
design-freedom delegation to 5.5 runs hotter than doctrine assumed.
Every layer produced unique catches this session; no drop candidates.

## C-015: Benchmark expansion council — suite architecture v2 + interop (2026-07-08)

FULL ENTRY (genuine deliberation; same-day second convening after
C-014). Convened on Ed's directives: (1) an extensive review of what
scientific questions the benchmark can answer and what measurements are
being left on the table; (2) expansion toward multi-prompt suite runs of
varying difficulty/type and benchmark interop in both directions;
worktrees + liberal Codex agents authorized. Shape: two reach lenses
(R1 affirmative capability map; R2 missing measurements), two design
lenses (E1 suite architecture/statistics; E2 interop), lead synthesis,
peer counterreview with design judgment invited, lead adjudication.

Reach outcomes: R1 mapped every answerable question by claim ceiling
(today / Window A / Window B / hardware-gated) with ladder-compliant
claim templates — landed as the bank's capability-map section; its
verdict named three unscheduled cheap campaigns (C5-1.6/1.12/1.8),
queued as ONE select-after-floors row (P2-024). R2's
collect-now-or-lose-comparability set (per-bundle env snapshots,
cooldown-trace preservation, inter-run gaps, tokenize/setup phase
markers, MLX memory snapshots, sampler-availability metadata) spawned
the window-a-capture worktree stream the same hour — the class of
finding that had to precede the 2M corpus' birth.

Design outcomes (consensus; peer narrowed, did not overturn): suite
architecture v2 (D-040 — B x k with r_within=1, bundle-level n,
one-mechanism architectural line, k=24, difficulty as quarantined
metadata); interop direction (D-041 — thin import manifests, HumanEval
smoke first, marker-shim energy layer with a verdict-shaped spike,
export prioritized for adoption-per-build-day, kill list). Peer's
unique catch: PER-ITEM FAILURE ECONOMICS — without a per-item
validity/status model + aggregation rules, suite breadth creates
ambiguous partial evidence; adopted into the P2-010a substrate
definition. Peer also drew the capstone stop-line (guaranteed capstone
= instrument + Mac characterization; expansion drops first under
pressure) and restated the D-034 gate — both landed in the 2O plan.

Layer yield note: all four lenses + peer produced unique catches;
the invited-peer pattern again narrowed designs materially (minimal-
substrate cap, energy-layer-only pin, gate amendment). Zero dissent
recorded; the round's three open design questions (substrate scope,
import-vs-export priority, capability-map home) resolved in one
counterreview pass without a second discussion round. A post-landing
verification workflow (3 lenses + refuters) then caught one blocker
(the 2O section retaining the superseded C-014 substrate enumeration)
and six should-fixes (level-marker omission vs AP-5, D-039-allowlist
drift worded as restatement, lossy D-041 kill-list record, an inflated
HumanEval floor claim, unlanded R2 dispositions, P2-010 gate omission)
— all fixed pre-commit; the verification layer earned its keep on its
first C-015 outing.

AMENDED 2026-07-08 (suite-build adjudication, D-044..D-047): the C-015
minimal-sketch is amended in three adjudicated ways — per-item response
TEXT ratified into `outputs/suite_items.jsonl` (D-045.8), the
`markers:`/`outputs:` blocks pinned as optional-defaulted-validated
constants inside the hashed effective manifest (D-044/D-045.3), and an
additive per-item `prompt_token_ids` source added for ids-native
sentinels (D-045.5/D-046). Dispositions for all 37 research-report
amendments: suite_implementation_research.md §Adjudication.

## C-017: Suite-build adjudication + implementation gates (2026-07-08)

Shape: Codex disposition draft over the 37 unresolved research-doc
amendments (invited design judgment, 8 argued lead calls) → lead
decisions → fresh Codex adversarial round on the decision batch →
implementation in 3 streams (substrate 3 units; affine; generators) each
with 2-3 fresh lenses + fix rounds → 1 Opus fresh-eyes substitute during
a Codex quota outage → 7-reviewer pre-merge oversight → 3 final-head
passes → post-merge integration review. Full narrative + per-layer catch
rows: `docs/run_reports/2026-07-08-suite-build.md` (process trace
appendix).

Genuine deliberations (positions moved): A3 manifest identity — lead
proposed raw-file-bytes hash, counterreview AMENDED to the canonical
EFFECTIVE-manifest hash (defaults inside identity; accepted, D-044); B5
BOS parity — lead DEVIATED from the draft's BOS-normalize
recommendation to ids-native-all-five (control must remain the incumbent
stream byte-for-byte); attack sustained with a binding
non-generalization caveat (D-046). Affine sentinel redesign: lens caught
that tag-forced duplication corrupted level denominators; lead chose the
dedicated-sentinel-item shape over relaxing SUB-1 (D-047.2 amendment,
k=25/26).

Layer yield (unique catches): lead live gates 3 (all
integration-reality class: cwd refs, strict rollup provenance, sampler
API namespace — invisible to 680+ unit tests and 9 lenses); oversight
10+ (incl. two validation holes: tamperable rollup digest,
vanishing group markers); unit lenses ~20; Opus substitute 1 major
(tokenize-window bracketing, FakeClock-blind); adversarial adjudication
round 4 (effective-hash identity gap the standout); integration 0
(clean). Process slip recorded: PR #18 merged into its stacked base
(retarget missed); recovered same session via promotion PR #20; lesson
folded into multi-stream-worktrees skill.

Addendum (2026-07-09, C-027 review, MET-001 / REV-4): the PR #18 merge
fdcf800 landed into suite-substrate, not main, and required promotion
PR #20 (84a70ca) to recover. Reclassified from operational "slip" to a
MERGE-GATE BREACH: D-031 requires PRs to land to main, and the merge
gate requires sibling merge-order simulation, which would have caught
the wrong base. Code outcome was fully recovered; the gate failure
stands as recorded. No history rewrite.

## C-018: D-013 alignment-capture window fix (2026-07-08)

Shape: background-chip session for the C-017 oversight spin-off
(alignment capture inside the measured window; predates the suite
substrate, since de5f04a). Solo lead implementation — a two-line
reorder in `_stage_measured_run` (stamp `sampling_stopped_s` as soon
as the runtime returns, then capture alignments) plus two regression
tests (`AlignmentCostTelemetry`: costly `clock_alignments()` must not
change metrics or move the stop marker) — with one light Codex
read-only review of the final diff (timing-semantics-adjacent, so the
cross-model pass ran despite the small size; no council per rule 3).

Layer yield: the catch itself is credited to the C-017 oversight
layer. This session: lead live verification proved both tests fail
pre-fix (gross_energy_j 0.84 -> 38.34 J under a 5 s simulated capture
cost) and re-ran the full suite (734 green); Codex review returned
approve with zero findings (it independently re-checked
`measured_window()` in bundle_read and the failure-path stop helper).
Landed: PR #21.


## C-019: Post-suite-build meta-reassessment (2026-07-08)

Standing §10 trigger (multi-PR session; Ed directed the full run after the
parallel alignment-fix session landed as PR #21). Shape: 4 parallel Codex
analyst lanes + completeness critic; lead synthesis. Lane outputs
preserved in the session scratchpad; conclusions and dispositions here
and in the run-report addendum.

Lane findings adopted:
- 5.5-DIRECTION STUDY (priority lane, 43 invocations deep-sampled):
  direction doctrine distilled and FOLDED into the codex-delegation
  skill — precedence sentence, autonomy clause, FIX-N fix contracts
  (7/7 one-shot), angle-named lenses, production-shaped gate
  requirement, checks-performed line for CLEAN verdicts, stack-context
  for reviewers; RELAX list (invariants not structure; shorter reads
  when facts embedded; early design-freedom). Post-upgrade expansion
  candidates recorded with safety gates; calibration labels declared
  MODEL-VERSION-SCOPED with a sealed-A/B re-baselining rule before any
  boundary move (critic item 1).
- CALIBRATION LONGITUDINAL: design-freedom-runs-hot confirmed across
  C-010/C-014-15/C-017 (high judgment yield, gates still mandatory); no
  active layer at two consecutive zero-catch sessions; WATCH items:
  integration-after-clean-oversight (one zero at C-017, C-010 contra),
  Opus-vs-Codex fresh-eyes A/B (sealed same-packet protocol defined; ≥2
  trials before roster change). Prompt-defect class active (~2/large
  session, lead-side); quality denominator (false-positive burden,
  severity mix, triage cost) noted as missing instrumentation (critic 7).
- PROJECT STATUS: the guaranteed capstone hinges on the 2M corpus; the
  critical path is P2-015 floors → P2-006 2M → baseline_results.md →
  Phase-4 claims scaffolding. P1-008 calendar mapping ELEVATED to
  ED-EXTERNAL rank 1 and extended with the evaluator acceptance-bar ask
  (critic 8). P2-025 re-ranked adjacent to the real-tokenizer manifest
  work. R-012 schedule risk named the biggest active management risk;
  R-016 interim backup becomes serious before 2M.
- CLOSURE: D-013 prose/docstrings back-annotated to marker-bounded
  wording (this batch); C-018 index row added with commit hashes;
  RUN_STATE 734; bank affine-queued line amended. Derivability clean.
- CRITIC dispositions: (1) sealed A/B re-baselining ADOPTED (skill);
  (2) pre-#21 bundle validity — alignment-capture overhead is
  dict-read-scale, corpus remains claim-usable, recorded here, no
  re-reduction; (3) quiet-window/upgrade-exploration conflict — upgrade
  experimentation is [AGENT]-lane, never in quiet windows (C-009 T5
  extends); (4) post-merge SHAKEDOWN GATE adopted into P2-015 row (one
  tiny production-shaped campaign-runner run before Window-A data);
  (5) skill folds listed with paths in the run-report addendum;
  (6) site regen rides this batch; (7) noted above; (8) adopted into
  P1-008.


## C-020: Stop-and-analyze whole project — technical + research merit debate (2026-07-08)

Event class: owner-directed whole-project merit review ("strictly
technical and research merit; logistics off-limits; split study is
happening"). Largest review event to date: a 69-agent Workflow (5 codex
readers over all top-level docs + code + evidence, 2 web freshness scans
[2026 energy-benchmark landscape; split-inference energy literature],
5 assessment lenses [technical feat / benchmark merit / audience /
research questions / skeptic], per-finding adversarial verification
tiered by materiality, synthesis + attack round), PLUS two independent
Fable position papers (session lead, written pre-workflow-output; fresh
Fable subagent with no session context), PLUS a recorded Fable-vs-Codex
debate round and lead adjudication. Artifact: the corrected assessment
is committed at docs/reviews/2026-07-08-technical-merit-review.md;
position papers and debate transcripts in the session scratchpad;
verdict summary in the run-report addendum.

CONVERGENCES (all three poles independently; no debate needed):
- The distinctive technical feat is the composed EVIDENCE ARCHITECTURE
  (auditable raw-to-claim chains, marker-bounded windows, strict
  re-derivation) plus the clinical-trial-style claim-gating stack
  (ladder/floors/pre-registration) — plausibly field-first for energy
  benchmarking; the components individually are well-executed-standard.
- Machinery is ahead of data: ~six real bundles gate hundreds of pages
  of methodology; nearly all research merit is promissory until the
  campaigns run. Correct failure mode for this stage, but graded as
  instrument + de-risked path, not results.
- Sensor trust (vendor telemetry, uncalibrated) is the binding validity
  ceiling; the wall/USB-C bridge is load-bearing methodology.
- Pre-registering a compositional split-energy prediction before split
  hardware runs (lead Thesis 5 = fresh-Fable "spine inversion" = Codex
  "elevates Q1 to transferable theory") → promoted as D-048.

DEBATE RULINGS (lead adjudication after Codex round 1; dissents kept):
- D1 question ranking: coupled Q4→Q1 (compositional prediction +
  first-of-kind per-stage dataset) #1; TOKEN-SHAPE SUFFICIENCY NULL
  SUSTAINED at #2 over fresh-Fable's omission (equivalence-margin
  results travel: a holding null validates every shape-matched synthetic
  energy workload; a failure confounds every shape-only benchmark); Q6
  boundary bias ELEVATED to #3 (fresh-Fable's "most citable by other
  benchmark authors" conceded by Codex); active-parameter scaling #4;
  affine ladder reclassified per D4; Q5 last ("unresolved ties" likely;
  the MDE discipline is the contribution, not the answer).
- D2 crossover prior: fresh-Fable CORRECT against the original Codex
  draft — debate arithmetic (Qwen2.5-1.5B: 28,672 B/token → 56 MiB @
  2048 tokens → ~0.5 s on 1GbE; 8B @ 8192 → ~9 s; second-device
  overhead 5-50 W → 2.5-25 J against tens-of-joules prefill savings)
  places crossover as possible-not-uniform: favored by asymmetric
  device strengths, long prompts, ≥2.5GbE, low-idle pairings. This
  arithmetic is why D-048 is mandatory, not stylistic.
- D3 spine: synthesis adopted — model-first FRAMING, dataset-first
  CONTRIBUTION (thesis sentence in D-048). Fresh-Fable's strong
  inversion declined: the both-end per-stage decomposition dataset is
  first-of-kind regardless of model fit.
- D4 affine ladder: lead position sustained — a suite-validity and
  denominator-discipline instrument, not a headline; C5-1.9
  (MoE-vs-dense energy-per-correct) exempt. Codex conceded its stack
  overstated the ladder's scientific independence.
- D5 cheap validity moves, priority: (1) publish a bundle pack + obtain
  ONE external strict re-reduction (fresh-Fable: "auditability is an L0
  claim until an outsider re-reduces a bundle" — conceded by Codex as
  the cleanest new criticism of the debate); (2) USB-C PD / wall
  cross-check; (3) same-class unit-to-unit CV campaign. None upgrades
  today's claims; each raises the claim ceiling.

REPO-VERIFIED CORRECTIONS (attack round; applied to the review doc):
bundles are gitignored/unpublished (external auditability never yet
exercisable); NO LICENSE file (blocks all external adoption; owner
decision); D-033 strict-validation legacy bypass (absent
summary_provenance skips workload-provenance checks — known tamper
hole, queue row); gating stack is partially exercised (D-014 protocol +
MDE sizing ran on real data; the floor gate itself has never fired);
contamination catches were one human + one automated (not two
automated); Jetson leg is a physical shunt measurement, not a vendor
model — the program's sensor taxonomy is mixed, not uniformly modeled.

DISSENTS RECORDED: fresh-Fable maintains full spine inversion (thesis =
model, not dataset); fresh-Fable's Token-Shape omission overruled;
original Codex-draft optimism on the uniform crossover prior overruled
by its own debate arithmetic.

PROMOTED: D-048, D-049. Queue rows: D-033 bypass fix, bundle-pack
publication prep, split-prep AP-row obligation, PROJECT_STATUS
orchestration-surface trim. Owner items surfaced (not queued as
blockers per scope rule): LICENSE choice; USB-C PD analyzer; external
re-reducer recruit.

## C-021: Advisor status-site live-depth refresh (2026-07-09)

Pointer entry. Full narrative and verification live in
`docs/run_reports/2026-07-09-advisor-status-site.md`; decision policy is
D-051.

Shape: Codex implementation stream over the Lakebed capsule and generated
site, with a separate gpt-5.5-high read-only counterreview before deploy.
The work was intentionally deployment-scoped rather than research-scoped:
make the advisor preview harder to stale, easier to scan live, and deeper
without moving source-of-truth status out of the repository.

Resolution:
- Keep generated static pages as the audit fallback; do not make Lakebed a
  parallel project-status database.
- Add `/api/live-status` as a fail-soft overlay parsed from current GitHub
  markdown for `PROJECT_STATUS.md`, `RUN_STATE.md`, `TASK_QUEUE.md`, and
  `docs/risk_register.md`.
- Expand the generated status cockpit with advisor attention, campaign
  readiness, evidence, and claim-ceiling panels.
- Remove volatile hand-authored counts from the Story page unless they are
  generated or source-linked.

Dissent: none recorded before deploy; counterreview findings, if any, are
adjudicated in the run report.

## C-023: Scientific-rigor review — suite, benchmark, question bank (2026-07-09)

- Date: 2026-07-09. Participants: Claude Fable (lead adjudicator), 4 fresh
  gpt-5.5-high read-only lenses (L1 metrology, L2 benchmark/statistical
  design, L3 question-bank audit — every question individually, L4
  Stanford-PhD-EE advisor simulation), 1 fresh gpt-5.5-high discussion
  instance (D1) arguing the lead's synthesis with doc-verification duty.
- Full record with verbatim lens outputs:
  `docs/reviews/2026-07-09-scientific-rigor-review.md`. Review-only
  session: no code changed, no worktrees (read-only fan-out per
  codex-delegation §Parallel threads).

Question: steelman the methodology, scope, and objectives; does the
project as specced (hardware openly not in hand) stand up to a
Stanford-PhD-EE advisor?

Resolution (lead, with D1 concurrence):

- Today: strong PROVISIONAL methodology; simulated advisor withholds
  final sign-off on specific, curable grounds.
- All blocker-class gaps are software/spec-only: B1 metrological error
  budget + uncertainty propagation; B2 benchmark-level multiplicity /
  analysis registry; B3 canonical RQ registry (bank overgrown, aliases
  unnormalized); B4 frozen capstone headline + minimum-viable-capstone
  contract. With those landed, both models independently answer YES at
  the advisor bar, under the headline "auditable, boundary-labeled local
  LLM energy characterization on named stacks" with split inference as
  gated stretch.
- Design-bearing majors accepted: contrast-level inference replaces
  "intervals separate" (amends D-014 wording when adopted); ordering
  executability before any suite campaign (C-015 rotation promise vs
  sequencing-spec manifest_order — elevated by D1); token-normalization
  contract + stack-identity table; phase-window claim gate; thermal
  proxy honesty; per-backend telemetry-trust caveats + pre-registered
  calibration runbooks.
- Discussion catches (the review system working both directions): D1
  OVERTURNED the lead-accepted C5-1.1 attribution blocker by citing the
  existing C-014 amendment + claims-ladder forbidden language (lead
  verified and accepted — naming hygiene only); D1 reordered the lead's
  pre-hardware work plan (headline first, P2-015 as combined
  floor+calibration+trust+error-budget spec, stats amendment before
  reducer code, campaign packs last behind a registry/linter cut-line).
- Unique catches by layer: L1 error budget + idle-model + phase-gate;
  L2 multiplicity + contrast-rule + ordering gap; L3 registry gap +
  per-question table + coverage gaps (telemetry perturbation, version
  drift, jitter sensitivity, output-token identity); L4 frozen headline
  + MVC contract + stack-identity table; D1 the C5-1.1 overturn + plan
  reorder. Zero-yield layers: none.
- Dissents: none unresolved after one discussion round.
- Queue impact: deliberately NOT applied — the recommended work order is
  input to the user's next planning session (spec fleshing for all
  no-hardware pieces), per the user's two-step directive.


## C-024: Spec-fleshing wave 1 — no-hardware artifact build (2026-07-09)

Pointer entry. Full narrative and verification:
`docs/run_reports/2026-07-09-spec-fleshing-wave1.md`; decisions
D-052..D-055; review inputs from C-023.

Shape: lead-driven, four worktree streams implemented by gpt-5.5 against
the C-023 packet (scope/headline, P2-015 combined floor design, stats
amendment + analysis registry, canonical RQ registry), each with a fresh
read-only counterreview lens, FIX-N rounds for accepted findings, a fresh
final-head pass per branch, a tail-verification pass over post-review
commits, CI, self-merge under the standing authority, and one post-merge
integration review (5 seam findings, fixed same-session).

Dissent: none unresolved. Notable adjudications: R2 estimator kill
accepted (floor redefined as false-effect guard); FH ledger-promotion
blocker resolved by supersession annotation per the history rule, not
rewrite; R4's bank-cited un-merge of C5-W.3 from Q5 overrode the original
C-023 lens's duplicate call.

Addendum (2026-07-09, C-027, MET-001 / REV-12): C-024 records "3 fix
rounds" while its run report records fix units F1-F6 ("6 fix
rounds", counted as 6 in the session total). Clarification: the
records do not conflict — the session ran 3 chronological fix ROUNDS
comprising 6 fix UNITS: round 1 = F1-F4, one per-stream fix pass
after the four counterreview lenses (scope, p2015, stats, rqreg, run
in parallel); round 2 = F5, the p2015 tail fix; round 3 = F6, the
integration fixes (per the wave-1 report's F1-F6 row, "6/6 one-shot
clean", and its yield line "6 fix rounds incl. integration").
Convention going forward: council log counts ROUNDS; run reports may
additionally count UNITS and must label which they are counting.

## C-025: Wave 2 — ultracode workflow build (2026-07-09)

Pointer entry. Full narrative and verification:
`docs/run_reports/2026-07-09-spec-fleshing-wave2.md`; decisions
D-056..D-059; work order from C-023 via C-024.

Shape: first Workflow-orchestrated build (46 agents: 4 codex implement
streams in worktrees -> 2 lenses each with stream-specific angles ->
severity-tiered adversarial refuters: blockers 2, should-fix 1) plus two
lead-driven reinforcement streams (claims linter pulled forward from the
cut-line; RQ-ENERGY-VARIANCE candidate design from Ed's variance
question), then per-stream fix rounds, lead gates (suite + live e2e on
the lead's shell, incl. strict-validating live rotated campaign
bundles), 6 fresh final-heads, a combined tail-verification pass, a
throwaway combined-ref merge + full suite BEFORE merging (C-022 lesson,
first deliberate use), CI, self-merges, and one integration review with
live rotated-campaign interaction checks.

Notable: the design-round-first flow (Ed's directive, folded to
operation-loop §4a) ran on P2-030 — 5.5's design memo ratified with pins
before implementation; zero design rework followed. Codex worktree
commits remain sandbox-blocked (index.lock) despite git permissions —
workflow wrapper agents committed/pushed; lead pathspec commits for
direct codex-run streams. PROCESS DEFECT recorded: the lead ran its
bookkeeping edits concurrently with a workspace-write codex fix round in
the SAME main tree; the fix round's cleanup reverted the uncommitted
bookkeeping (recovered same-session from in-context content) — the
two-writers rule applies to the LEAD as well; bookkeeping waits for tree
quiescence. Dissents: none unresolved.


## C-026: P2-034 broad campaign packs (2026-07-09)

Pointer entry. Full narrative:
`docs/run_reports/2026-07-09-p2034-broad-packs.md`. Design round
ratified with three lead pins (unnamed second-family placeholder;
runtime-held-constant = revision/build-family; smallest
method-transfer suite first for C5-3.5); no new decision-log entries
(pack content rides ratified contracts). Dissents: none.

## C-027: Whole-project council review with gpt-5.6-sol (2026-07-09)

Full record: `docs/reviews/2026-07-09-c027-whole-project-review.md`
(disposition table for all ~80 lens findings, per-blocker verification
lines, deliberation traces). Raw lens/counterreview/examiner outputs
archived under `docs/reviews/c027/`. This entry records only the
genuine deliberation.

Participants: Fable 5 lead; Codex gpt-5.6-sol xhigh (FIRST production
session of the new model; CLI upgraded 0.143.0→0.144.0 mid-session
after the old CLI rejected the model) — 7 read-only lenses + 1
counterreview; 1 fresh-context Fable-tier final examiner. Scope
declaration: all peer passes were STATIC-ONLY and single-model-family —
execution behavior, SSH-path security, and licensing were reviewed by
nobody and are recorded as open debts, not clean.

Positions → resolutions (design-bearing only):

- Legacy-gates framing: lead draft said the six real bundles "failed
  the advertised gates"; counterreview showed D-037 binds from 2M
  onward, so the correct frame is legacy L1 + manual waivers —
  counterreview PREVAILED (the lead's framing would have manufactured
  an ex-post-protocol defense problem).
- Process-restructure staging: lead deferred the machine-readable state
  kernel; counterreview argued deferral leaves the demonstrated drift
  mode active and that policy generation is the harder half —
  counterreview PREVAILED; kernel is Stage 1 (D-063 records the
  reversal).
- Layer-drop rule: lead's "3 applicable sessions, severity-weighted"
  was attacked as reintroducing post-hoc discretion; adopted WITH the
  peer's mechanical-predicate construction (D-061).
- ARCH severity: undifferentiated blocker trio split into immediate
  (zero-window, P2-040) vs NVIDIA-gated (NV-GATE-2) per counterreview.
- Sequential sampling: fixed-n + explicit demotion adopted over both
  status quo and default alpha-spending (D-062); peer confirmed the
  demotion rule is coherent only with its four explicit clauses.

Layer yields (C-027): lenses 8 confirmed blocker clusters + ~60
accepted findings, 0 verified false positives (blocker tier; lower
tiers unaudited); counterreview 3 synthesis blockers (2 were LEAD
errors — the only confirmed review errors this session were the
lead's); final examiner 8 dropped/under-tiered findings + the
validity-threats section, all adopted. Reverse-review layer indicted
the lead's own conduct (empty D-050 manifest, four D-031 direct-to-main
commits) — accepted in full, remedies in MET-001/RETRO-001.

Dissents overridden: none unresolved. Lead notes for the record: ARC-1/2
remain hard acceptance gates at NVIDIA live promotion despite the
severity downgrade.

Calibration (model-version scoping): one promising 5.6-sol batch —
9/9 OK exits, ~28 verified file:line claims all accurate, unprompted
premise correction (5 instances), the counterreview out-argued the lead
twice. NOT a promotion; the pre-registered sealed A/B remains the gate
before delegation-boundary changes.

---

## Full entry

## C-028: C-027 adjudication and integration arc — infrastructure wave, PRs #49/#54/#55, and the integration window (2026-07-10/11)

Full record: `docs/run_reports/2026-07-11-c028-continuation.md`; binding
rulings: `docs/specs/c027/ADJUDICATION.md`. No tracked
`docs/process_traces/` artifact is present in this checkout; the run report's
aggregate invocation record is therefore the durable evidence available for
this arc, and D-064 governs future tracked event streams. This limitation is
recorded rather than repaired with an invented pointer.
The arc's earlier segment (adjudication rounds, PRs #41–#48) is
recorded in the CP-5/checkpoint records and stop-card history; this
entry records the 2026-07-10/11 continuation.

Participants: Fable lead; gpt-5.6-sol as implementer, reviewer,
refuter, auditor, and design consultant across ~57 recorded
invocations. The lead retained worktree/merge authority, every final
diff gate, all live verification, and bookkeeping.

Scope of this segment: PR #49 (NV-GATE-2 code-now + flake
root-causes) merged `1b0f1f6` + `10e0ad2`; PR #54 (P2-041 vetted
rebuild from the RED-tranche triage recipe, review + fix round +
delta review) merged `69a3393`; PR #55 (P2-044 idle dependence /
HAC / ESS, design-consult-first, review + fix round) merged
`56d103e`. At the Ed-directed pause (stop card checkpoint #4 +
amendments) PRs #50–#53 and #56–#58 stood open and lead-gated with
the resume order pinned; after resume, the integration tree
(`c028-integration` @ `190a0fc`, main post-#55 + 7 branches) caught
38 cross-stream failures, the fix round + cross-stream review
cleared them, and the full wave merged SHA-guarded (#50, #51, #52,
#53, #56, #57, #58 — P2-037 last), with final main verified green
and content-identical to the reviewed tree; follow-up PR #59 (from
the cross-stream review) is under review and DOC-008 rounds remain
in flight. Delegation infrastructure landed on main: adapter,
codex-run-v3, usage guard, scope backstop.

Closeout amendment (2026-07-11): C-028 is **CLOSED**. PRs #41-#58 are
merged; current main's canonical suite is 1,220 OK (`skipped=10`) and the
corpus gate is 6/6. PR #59 remains open with a 1,224-test green worktree
replay (`skipped=12`), and `impl/doc008-kernel` is pushed awaiting PR. These
open follow-ups do not reopen the card. Every Window-A software gate and
P0-003 are satisfied; quiet-machine execution with Ed remains deliberately
separate from landed-software status. NVIDIA/Orin protocol pins remain
PROVISIONAL pending live evidence.

Layer structure: Sol implementation sessions (xhigh; 2 ultra for the
p2041-vetted composition and the P2-037 engine) → review lenses
(contract + semantics per stream) → severity-tiered refuters (2 per
blocker) → independent post-hoc audits (P2-037) → delta re-audits
after fix rounds → lead gates (live runs, arithmetic checks, final
heads, CI) → cross-stream integration tree before each merge.

Unique catches per layer (D-061 evaluation record):

- **Sol merge review:** caught the lead's own merge-resolution
  error — the branch's updated P2-005 row silently lost by a
  whole-file `--theirs` checkout during the #49 conflict
  resolution; repaired as a proper 3-way merge (`13f6c9e`). Only
  layer to catch it.
- **Refuter tier:** narrowed 2 blockers via CONTRADICTORY paired
  verdicts — P2-041 B1 (contract refuter confirmed, reachability
  refuter refuted the broad form → landed as the narrowed shared
  fail-closed cooldown verifier, `f2c4701`) and P2-037 F1 (design
  vs repro refuters split the same way → F1 narrowed before the
  fix round). The disagreement itself was the signal; neither
  single refuter would have produced the narrowed form.
- **Delta re-audits:** 2 fresh blockers in paths newly reachable
  only after the fix round (P2-037 delta re-audit:
  blocker=2/should-fix=3), plus the recurring symlink pattern —
  cooldown provenance `Path.resolve` unwrapped against symlink
  loop/OSError, wrapped fail-closed with a cross-version
  regression test (`5f1f161`). Neither finding existed in the
  pre-fix tree; the re-audit layer is what sees post-fix
  reachability.
- **Lead gates:** P2-044 F1 cadence arithmetic verified directly
  (all-intervals population; binding Qwen-r3 values asserted
  exactly: median 0.1199250625, ratio 1.0581313969 — `dc1ab95`);
  live NV-5 localhost gate 3/3 OK closing the open lead gate on
  #49 (`10e0ad2`); live doctor run. All three are
  lead-live-only — no static layer could produce them.
- **Integration tree:** 38 pre-merge cross-stream test failures
  caught at the combined head, dominated by REPRO-002's
  fail-closed environment/inventory checks meeting post-cut fields
  from sibling streams. Zero of these were visible in any single
  stream's green suite.
- **Enforcement layer (scope backstop, live):** 2 bytecode
  false-positive firings tuned same-day; NEEDS_SCOPE compliant
  stops ×3 (p2037 fix round, doc008 ×2) — each returning the
  correct paths where the lead had guessed wrong.

Scope enforcement fired in production: two sessions (p2043-impl,
p2044-fixround) exited SCOPE_VIOLATION with work preserved in
evidence bundles, not landed; one wrapper crash (lead in-place edit
of the installed runner mid-run) was recovered via a lead-authored
recovery row rather than a mutated record — both behaviors are now
ratified in D-064.

Rough spend (from the two manifests + local usage accounting;
estimates, not billing truth): 2 ultra sessions ≈ 100M tokens
(p2041-vetted composition, P2-037 engine); 53 recorded xhigh
invocations (14 v2-manifest + 37 v3-event-stream + 2 transition-era
rows) — local 24h accounting shows 50 xhigh sessions ≈ 171M tokens;
2 high (both FAILED rc=1 resume attempts, work recovered in later
sessions) ≈ 40M. Fable lead: ~1.8M generation / ~14.8M billed-ish /
~570M cache reads. Two v3 sessions (doc008-r3, pr59-review) still
RUNNING at the manifest snapshot.

Spend snapshot addendum (2026-07-11 ~20:00Z, `codex-usage` 24h
window, arc-close truth for the table above; estimates, not billing):
59 Sol sessions / 330.6M tokens / ~17.5h session time — xhigh 55 ≈
190.4M, ultra 2 ≈ 100.3M, high 2 ≈ 40.0M (both FAILED). Composition
(measured from raw session records): ~97.4% of Sol input is cached,
output ≈ 0.37% of volume. API-list-price equivalent (GPT-5.6-sol
$5/$30, cached $0.50; Fable 5 $10/$50, cache reads $1): Sol ≈ $240,
Fable ≈ $810 — combined ≈ $1,050 for the recorded arc; upper bound
≈ $2,300 counting all local Codex sessions (includes non-manifest
sessions; resume rows may double-count). Note the inversion: Sol is
~180x the token volume but Fable is ~3.4x the cost — cache reads
dominate the lead's footprint. Snapshot convention now standing in
the council skill §Recording + instrumentation.

Process artifacts adopted this arc (ratified as/alongside D-064):

- **claude-codex-report/v1** — canonical machine-parsed session
  report envelope; run_finished rows record parse validity, finding
  counts, verification counts, scope flags.
- **codex-run-v3** — append-only event-stream manifest
  (run_started/run_finished/run_consumed), retry-with-resume,
  lead-authored recovery rows on wrapper failure.
- **WRITE_SCOPE backstop** — post-run diff vs declared scope; exit
  77 + evidence bundle on violation; NEEDS_SCOPE prospective-only
  expansion (AGENTS.md precedence section, `9ca89cc`).
- **NEEDS_RULING** — any blocking non-delegable decision
  early-returns a structured question instead of a guess
  (`31b3f5e`); usage guard + usage-pressure mode active.
- **Design-consult-by-default** — Ed-prompted global-rule
  amendment; exercised for P2-044 (HAC/ESS design consult,
  `827df12`) before implementation.

Dissents overridden: none unresolved. The P2-041 RED tranche
(ultra round deleting P2-038/P2-040 wholesale) was not landed or
argued — it was triaged per-file and rebuilt from main under three
Ed-approved C rulings (`96e10bd`, `750f7d0`).

Calibration note (model-version scoping, per C-027): the refuter
contradictory-verdict pattern produced correct narrowings twice;
the two scope violations and one thin-output ultra warning are the
arc's recorded 5.6-sol failure modes. Sealed A/B remains the gate
before any delegation-boundary change.


exec
/bin/zsh -lc "sed -n '1530,1890p' docs/council_log.md" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
## Full entry

## C-028: C-027 adjudication and integration arc — infrastructure wave, PRs #49/#54/#55, and the integration window (2026-07-10/11)

Full record: `docs/run_reports/2026-07-11-c028-continuation.md`; binding
rulings: `docs/specs/c027/ADJUDICATION.md`. No tracked
`docs/process_traces/` artifact is present in this checkout; the run report's
aggregate invocation record is therefore the durable evidence available for
this arc, and D-064 governs future tracked event streams. This limitation is
recorded rather than repaired with an invented pointer.
The arc's earlier segment (adjudication rounds, PRs #41–#48) is
recorded in the CP-5/checkpoint records and stop-card history; this
entry records the 2026-07-10/11 continuation.

Participants: Fable lead; gpt-5.6-sol as implementer, reviewer,
refuter, auditor, and design consultant across ~57 recorded
invocations. The lead retained worktree/merge authority, every final
diff gate, all live verification, and bookkeeping.

Scope of this segment: PR #49 (NV-GATE-2 code-now + flake
root-causes) merged `1b0f1f6` + `10e0ad2`; PR #54 (P2-041 vetted
rebuild from the RED-tranche triage recipe, review + fix round +
delta review) merged `69a3393`; PR #55 (P2-044 idle dependence /
HAC / ESS, design-consult-first, review + fix round) merged
`56d103e`. At the Ed-directed pause (stop card checkpoint #4 +
amendments) PRs #50–#53 and #56–#58 stood open and lead-gated with
the resume order pinned; after resume, the integration tree
(`c028-integration` @ `190a0fc`, main post-#55 + 7 branches) caught
38 cross-stream failures, the fix round + cross-stream review
cleared them, and the full wave merged SHA-guarded (#50, #51, #52,
#53, #56, #57, #58 — P2-037 last), with final main verified green
and content-identical to the reviewed tree; follow-up PR #59 (from
the cross-stream review) is under review and DOC-008 rounds remain
in flight. Delegation infrastructure landed on main: adapter,
codex-run-v3, usage guard, scope backstop.

Closeout amendment (2026-07-11): C-028 is **CLOSED**. PRs #41-#58 are
merged; current main's canonical suite is 1,220 OK (`skipped=10`) and the
corpus gate is 6/6. PR #59 remains open with a 1,224-test green worktree
replay (`skipped=12`), and `impl/doc008-kernel` is pushed awaiting PR. These
open follow-ups do not reopen the card. Every Window-A software gate and
P0-003 are satisfied; quiet-machine execution with Ed remains deliberately
separate from landed-software status. NVIDIA/Orin protocol pins remain
PROVISIONAL pending live evidence.

Layer structure: Sol implementation sessions (xhigh; 2 ultra for the
p2041-vetted composition and the P2-037 engine) → review lenses
(contract + semantics per stream) → severity-tiered refuters (2 per
blocker) → independent post-hoc audits (P2-037) → delta re-audits
after fix rounds → lead gates (live runs, arithmetic checks, final
heads, CI) → cross-stream integration tree before each merge.

Unique catches per layer (D-061 evaluation record):

- **Sol merge review:** caught the lead's own merge-resolution
  error — the branch's updated P2-005 row silently lost by a
  whole-file `--theirs` checkout during the #49 conflict
  resolution; repaired as a proper 3-way merge (`13f6c9e`). Only
  layer to catch it.
- **Refuter tier:** narrowed 2 blockers via CONTRADICTORY paired
  verdicts — P2-041 B1 (contract refuter confirmed, reachability
  refuter refuted the broad form → landed as the narrowed shared
  fail-closed cooldown verifier, `f2c4701`) and P2-037 F1 (design
  vs repro refuters split the same way → F1 narrowed before the
  fix round). The disagreement itself was the signal; neither
  single refuter would have produced the narrowed form.
- **Delta re-audits:** 2 fresh blockers in paths newly reachable
  only after the fix round (P2-037 delta re-audit:
  blocker=2/should-fix=3), plus the recurring symlink pattern —
  cooldown provenance `Path.resolve` unwrapped against symlink
  loop/OSError, wrapped fail-closed with a cross-version
  regression test (`5f1f161`). Neither finding existed in the
  pre-fix tree; the re-audit layer is what sees post-fix
  reachability.
- **Lead gates:** P2-044 F1 cadence arithmetic verified directly
  (all-intervals population; binding Qwen-r3 values asserted
  exactly: median 0.1199250625, ratio 1.0581313969 — `dc1ab95`);
  live NV-5 localhost gate 3/3 OK closing the open lead gate on
  #49 (`10e0ad2`); live doctor run. All three are
  lead-live-only — no static layer could produce them.
- **Integration tree:** 38 pre-merge cross-stream test failures
  caught at the combined head, dominated by REPRO-002's
  fail-closed environment/inventory checks meeting post-cut fields
  from sibling streams. Zero of these were visible in any single
  stream's green suite.
- **Enforcement layer (scope backstop, live):** 2 bytecode
  false-positive firings tuned same-day; NEEDS_SCOPE compliant
  stops ×3 (p2037 fix round, doc008 ×2) — each returning the
  correct paths where the lead had guessed wrong.

Scope enforcement fired in production: two sessions (p2043-impl,
p2044-fixround) exited SCOPE_VIOLATION with work preserved in
evidence bundles, not landed; one wrapper crash (lead in-place edit
of the installed runner mid-run) was recovered via a lead-authored
recovery row rather than a mutated record — both behaviors are now
ratified in D-064.

Rough spend (from the two manifests + local usage accounting;
estimates, not billing truth): 2 ultra sessions ≈ 100M tokens
(p2041-vetted composition, P2-037 engine); 53 recorded xhigh
invocations (14 v2-manifest + 37 v3-event-stream + 2 transition-era
rows) — local 24h accounting shows 50 xhigh sessions ≈ 171M tokens;
2 high (both FAILED rc=1 resume attempts, work recovered in later
sessions) ≈ 40M. Fable lead: ~1.8M generation / ~14.8M billed-ish /
~570M cache reads. Two v3 sessions (doc008-r3, pr59-review) still
RUNNING at the manifest snapshot.

Spend snapshot addendum (2026-07-11 ~20:00Z, `codex-usage` 24h
window, arc-close truth for the table above; estimates, not billing):
59 Sol sessions / 330.6M tokens / ~17.5h session time — xhigh 55 ≈
190.4M, ultra 2 ≈ 100.3M, high 2 ≈ 40.0M (both FAILED). Composition
(measured from raw session records): ~97.4% of Sol input is cached,
output ≈ 0.37% of volume. API-list-price equivalent (GPT-5.6-sol
$5/$30, cached $0.50; Fable 5 $10/$50, cache reads $1): Sol ≈ $240,
Fable ≈ $810 — combined ≈ $1,050 for the recorded arc; upper bound
≈ $2,300 counting all local Codex sessions (includes non-manifest
sessions; resume rows may double-count). Note the inversion: Sol is
~180x the token volume but Fable is ~3.4x the cost — cache reads
dominate the lead's footprint. Snapshot convention now standing in
the council skill §Recording + instrumentation.

Process artifacts adopted this arc (ratified as/alongside D-064):

- **claude-codex-report/v1** — canonical machine-parsed session
  report envelope; run_finished rows record parse validity, finding
  counts, verification counts, scope flags.
- **codex-run-v3** — append-only event-stream manifest
  (run_started/run_finished/run_consumed), retry-with-resume,
  lead-authored recovery rows on wrapper failure.
- **WRITE_SCOPE backstop** — post-run diff vs declared scope; exit
  77 + evidence bundle on violation; NEEDS_SCOPE prospective-only
  expansion (AGENTS.md precedence section, `9ca89cc`).
- **NEEDS_RULING** — any blocking non-delegable decision
  early-returns a structured question instead of a guess
  (`31b3f5e`); usage guard + usage-pressure mode active.
- **Design-consult-by-default** — Ed-prompted global-rule
  amendment; exercised for P2-044 (HAC/ESS design consult,
  `827df12`) before implementation.

Dissents overridden: none unresolved. The P2-041 RED tranche
(ultra round deleting P2-038/P2-040 wholesale) was not landed or
argued — it was triaged per-file and rebuilt from main under three
Ed-approved C rulings (`96e10bd`, `750f7d0`).

Calibration note (model-version scoping, per C-027): the refuter
contradictory-verdict pattern produced correct narrowings twice;
the two scope violations and one thin-output ultra warning are the
arc's recorded 5.6-sol failure modes. Sealed A/B remains the gate
before any delegation-boundary change.

## C-043: D-078 P0 instrument-repair close-out session — round-8 landing, round-9 final confirmation, sign-off (2026-07-22)

Shape: lead resumed the paused arc cold from scratchpad pointers; collected
the checkpointed Sol round-8 fix wave; §C-028 delta re-audit (3 fresh
read-only Sol lenses over a shared packet → 8 xhigh refuter verdicts,
blockers 2 refuters with distinct lenses); Sol xhigh round-8b fix wave under
enforced WRITE_SCOPE (one NEEDS_SCOPE early-return, lead-ruled, fixture fix
applied at the bench); bounded 8b delta re-audit; lead full-suite gates
(2081 → 2088 passed, 0 failures); commit `040ca3a`; round-9 FINAL
confirmation (Sol xhigh review genre); CR9-1 adjudicated as registered
limitation L1 per the loop-termination doctrine; close-out `debc6d2`;
PR #79 opened for Ed-named merge.

Layer catches (unique):
- Sol review lenses: A1 (v3 claim-eligibility contract divergence),
  B1 (ClockStamp physical-sanity gap → understated B_fiducial ~3 µs),
  C1/C2 (boundary float, OverflowError escape), C3/C4 (test-wiring gaps).
- Sol xhigh refuters: killed A2/B2 outright (both plausible, both wrong —
  A2's "legacy records break" was self-invalid synthetic-only; B2's
  stale-vs-invalid relabel would have broken a ratified distinction);
  narrowed C1 to a registered nit; split on A1 (contract-confirmed,
  reachability-refuted) — lead synthesis: pre-existing defense-in-depth
  hardening, not a round-8 regression.
- Round-9 confirmation: CR9-1 (floor artifacts self-attesting) — the only
  finding of the round, repro-backed, lead-reproduced at the bench.
- Lead unique: false-attribution triage of the 8b audit's two "blockers"
  (both were the lead's own authorized bench edits); the L1 adjudication.

Failure modes recorded: (1) upstream cyber-content filter killed 3/8
refuters mid-run on adversarial phrasing ("malformed/tamper/escape") —
rephrasing as data-quality QA of our own instrument recovered all three
(route: keep refuter briefs mechanism-neutral); (2) lead bench-edited the
worktree while an enforced-scope Sol session ran in it → false
SCOPE_VIOLATION attribution + resume-registry loss (rule: no lead edits in
a tree with a live enforced-scope session); (3) the known xhigh review-genre
null-final-message mode recurred on round 9; the documented bridge-resume
recovery worked first try.

Dissent recorded: the 8b delta auditor's should-fix (OverflowError
normalization also reaching v1 replay error behavior) was overridden by
lead ruling — frozen-replay doctrine protects computed semantics of
parsable artifacts, not crash reproduction on impossible inputs; the
reducer's structured-failure contract governs all protocols.

## C-044: NEG-8 estimand debate — peer disagreement adopted, Ed ratification (2026-07-24)

Ed directed a formal cross-model debate on the clause-10 ruling before
ratifying. Shape: lead position paper + explicit license and request to
disagree; one xhigh peer round evaluating five design options plus a
peer-proposed sixth; lead adjudication; plain-language synthesis to Ed;
Ed ratified the amended design with recorded guardrails (decision log
clause-10 addendum). Yield: the peer's structural correction (anomaly
screen must not erase drift from the claim budget) was adopted — the
second recorded case of invited peer design judgment beating the lead's
ruling. The debate also surfaced one gap neither model had specced
(drift-bound freshness horizon — prompted by Ed's own risk question) and
one open science question (a7-vs-a5 prefill floor scatter, 3x).
Calibration note: invited-disagreement debate briefs (steelman each
option, demand failure modes + examiner view) produced markedly higher
design yield than review-shaped prompts; adopt as the default shape for
estimand/contract rulings.

## C-045: NEG-8 screen+budget audit gauntlet — a new refuter pairing under A/B, four audit rounds, PR #85 (2026-07-24/25)

Shape: the Ed-ratified SCREEN + BUDGET wave (D-078 clause 10) was taken
through four adversarial audit rounds (fresh read-only Sol per round;
rounds 1–3 xhigh, round 4 high) with per-severity refuter tiers using a
NEW pairing under evaluation — **Opus-contract + Sol-execution distinct
lenses** (Ed-directed A/B; now the recorded default per the
instrument-mix-authority memory). Three Sol fix rounds (xhigh, xhigh +
a high alignment pass, high) plus lead bench fixes closed the findings;
two lead-owned decision-log addenda were written at the bench between
rounds. Commit stack on main(`125a48d`): `b120d07` wave → `69b65e5`
addendum 2 → `ad75542` fix round 1 → `315810a` addendum 3 → `a5a7acf`
capsule trim → `907ee58` fix round 2 → `dbf6339` fix round 3 →
`19e15d9` assertion restore → `60b12af` capsule pagination →
merged `c3e2647` (PR #85, 56 files, +6012/−439).

Layer catches (unique):

- **Auditor (fresh Sol, per round):** found real mechanisms in every
  round — round 1: estimand-dispatch downgrade (row shape selects the
  legacy gross-only evaluator), allowance fail-open (missing allowances
  silently become no allowance), anchor-gate bypass on the
  existing-bundle re-verdict path, and the refusal-registry gap (the
  authoritative registry test actually failed on
  `anchor_fallback_member_unusable`); round 2: coordinated-downgrade v2
  (strip basis *and* the whole drift group together) and the
  mock-label seam (`telemetry_source="mock"` defeats both dispatch and
  the anchor gate); round 3: TypeError on malformed basis values,
  telemetry-triangle downgrade into the frozen arm at the whole-window
  barrier, and loss of nonempty positive-path integration coverage;
  round 4: two omitted assertions in the replacement companion
  (nonempty affected-contrast set, `n == 5`). BUT it severity-inflated
  repeatedly — of 7 blocker-tier claims across rounds 1–2, refuter
  synthesis sustained 3–4 at tier (round 3 and round 4 produced no
  blockers at all: three should-fix, then one).
- **Opus-contract refuter (unique):** F2 collapse (the "broken frozen
  replay" blocker rested on a misreading of the freshness addendum's
  scoping — landed as a documented superseded gross-only wire, not a
  code fix); F6 refutation (condition-level distinctness was already
  contract-discharged at the consumer boundary); G1 re-price (the
  full-strip variant is a subclass of registered limitation L1, whose
  closure is queued as FLOOR-BIND-01, not a fresh blocker); G2
  re-price (the ratified non-mock carve-out plus D-030's
  strict/raw-evidence binding bound the exposure); blast-radius
  refutation of the auditor's proposed G2 fixture fix (strict
  validation binds backend raw evidence, so the naive fix breaks
  legitimate fixtures); **A1 terminal-mock-bar gap — the session's best
  catch**: an *honest* mock member could reach claim evidence with all
  mock-exempted barriers disabled, no attacker required; the NEG-8
  sentinel route on round-3 F2 (the one route with no downstream
  catch); and the F3 fixture-fix refutation (a production-promoted
  fixture cannot be strict-valid — use a patch idiom instead).
- **Sol-execution refuter (unique):** discovery of the
  coordinated-downgrade *variants* (strip the drift group and restore
  the headline floors and the record validates clean — reproduced on
  the repo fixture, gate `20.799350577898302 → 20.399350577898304`,
  exactly the fixture's 0.4 J allowance; asymmetric removal from the
  comparative record alone also validates clean); the G2A adjacent
  blocker (the reduce layer independently trusts metadata/summary
  mockness in the environment and CPU-admission barriers, so fresh
  re-reduction reproduces the forged exemption and strict
  stored-vs-fresh comparison is not a backstop); identification of the
  authoritative mockness source (custody-bound
  `config().hardware_target.telemetry_backend`, bound through
  `metadata.config_sha256`); the `mock:*` tagged-source class caveat
  (`axi_valid_burst` config `mock` vs summary `mock:target` — compare
  backend *class*, not raw strings); and every runnable probe,
  including the estimand-flip demonstration (`mock` → no refusals vs
  `powermetrics` → `whole_window_verdict_provenance_invalid` on
  identical evidence).
- **Lead (unique):** the two D-078 clause-10 registry addenda (2 and 3)
  — component-7 anchor-fallback gate ruling derived from the a7-vs-a5
  prefill-scatter root cause (a7's 11.85 J "floor" was one
  fallback-anchored member, r03; true floor ≈ 3.3–3.7 J), and the
  terminal mock bar; severity synthesis on the split verdicts (kept F4
  at blocker priority on imminent-use grounds against the contract
  refuter's downgrade); the capsule shard-budget trim (`a5a7acf`) and
  the pagination ruling that followed (deterministic `D-NNN`
  pagination + D-076 artifact-cap redirects); the battery-flake
  adjudications; and the bench fixes (registry clause, the fixture
  metadata line that blocked Sol's canonical run, the round-4
  assertion restore).

Rough spend (estimates, not billing truth): the gauntlet proper (audit
round 1 onward) recorded 11 distinct Sol wrapper invocations — 4 audits
(3 xhigh, 1 high), 2 execution refuters (both high), 3 implementation
rounds (xhigh; xhigh + a high alignment pass; high), 1 capsule session
(xhigh), plus retry attempts on two of them; counting the same day's
pre-audit wave, fold, fold2 and run-book sessions brings the day's Sol
total to ~15. Four Opus agents: three contract/design refuters (~96k /
120k / 144k tokens) plus one dictated-fills drafting/verification agent
(~115k) — the latter caught five material errors in the lead's own
dictation of this entry, including the effort-tier discrepancy ruled on
below. Lead orchestration on top. The
`codex-usage` ledger reads all zeros for the 5h and 24h windows ("local
quota signal unavailable in referenced session logs") — the feed is
suspected broken, so no token-volume snapshot is recorded this session.

Verdict: **the Opus-contract + Sol-execution pairing changed the triage
outcome in every round it ran** — it collapsed one blocker outright
(F2), re-priced two (G1, G2), refuted two proposed fixes before they
landed (G2 fixture, F3 fixture), and produced one blocker the auditor
never saw (A1 terminal mock bar). The two lenses split on G1/G2 (Sol
sustained both at blocker; Opus re-priced both) and the lead synthesized
rather than majority-voted, per §C-028. Adopted as the default
blocker-refuter shape; memory and skills to be updated by the lead.

Dissent recorded: on F4 the lead overrode the contract refuter's
downgrade and kept blocker priority, on the grounds that the
anchor-fallback replay path was about to be exercised by the next
window's re-verdict. On G1/G2 the lead implemented both fixes despite
the contract lens's re-price, treating the re-price as a scope
argument (what is *newly* broken) rather than a licence to defer.

Calibration note: the auditor layer's yield is real but its severity
calibration is not — four consecutive rounds produced findings worth
fixing while its blocker tier held at roughly half strength. The
refuter tier is what converts that into correct triage; running a
single-lens refuter would have inherited the inflation.

Effort-tier ruling (lead, flagged by the drafting agent's verification
pass): the execution refuters ran at `high`, not the
adversarial-review skill's `xhigh` default — deliberately in round 1
(Ed's A/B spec named "sol high") and carried into round 2 for
comparability. The A/B verdict therefore stands on high-tier refuters,
which is the STRONGER form of the result: paired distinct-lens
refuters at high changed triage outcomes that single-lens xhigh
refuters have historically missed. Ruling: in the paired-lens shape,
`high` is the default refuter tier; reserve `xhigh` for single-refuter
verification or judgment-dense standalone audits. The lead will amend
the adversarial-review skill's effort note accordingly.

Scorecard (dispositions per docs/orchestration.md): 20 findings raised
across 4 audit rounds incl. refuter adjacents. Accepted-and-fixed in
PR #85: 13 (r1 F1/F3/F4/F5/F7; r2 G1/G2/G3 + adjacent A1 terminal mock
bar; r3 F1/F2/F3; r4 F1). Re-priced by refuters before fixing: 4 of
those (r1 F4 blocker→should-fix; r2 G1/G2 blocker→should-fix; r1 F2
blocker→docs-only, landed as contract clarification). Rejected /
non-obligating: 2 (r1 F6 contract-refuted; r2-A2 traced not-reachable,
defensive comment only). Queued: 4 → kernel row CUSTODY-HARDEN-01
(G2A reduce-layer label trust, drift-bound seal authentication, dead
no-freshness accommodation, artifact_schema_invalid mislabel);
full-strip custody discrimination remains inside pre-existing
FLOOR-BIND-01/L1. Owners: all fixed items closed at merge c3e2647
(lead-verified); queued items owned by the kernel rows named above;
no open finding without an owner.

---


exec
/bin/zsh -lc "sed -n '1891,2117p' docs/council_log.md; sed -n '2118,2415p' docs/council_log.md; sed -n '2416,2598p' docs/council_log.md" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
## C-038: FLOOR-LABEL-01 gauntlet close + quiet-window collection — an instrument-mix re-proportioning, a lost quiet window, and two exit codes that lied (2026-07-25/26)

Shape: finish the FLOOR-LABEL-01 gauntlet (D-078 clause 11 — labelled
attribution-limited floors, unblocked by CAL-REBRACKET-01 / PR #86) and
then spend the quiet-Mac window collecting three measurement windows.
Lead instrument: **Opus 5 (1M context), effort `high`, confirmed by Ed
via the interactive `/model` command** (the TUI banner disagreed; see
`docs/process/model_allocation_ledger.md` §6 A-10). Mid-session Ed
**re-proportioned the instrument mix**: Opus 5 subagents become the
primary delegated lieutenant, Fable is consulted when genuinely needed,
Sol remains the execution workhorse, and the lead adjudicates rather
than performing the labor. The standing dictate is recorded in the
`instrument-mix-authority` memory and in the ledger §2 — this entry is
the first session run under it.

### Layer catches (unique)

- **Opus 5 contract lens** (subagent; ~164k tokens, 50 tool uses,
  ~11 min). Verdict **"COMPARATIVE COVERAGE: COMPLETE"** — it traced
  the labelled path end-to-end for comparative (ABBA) cells through
  extraction → canonical floor record → transport group → resolution →
  claim evaluation → final artifact. 4 should-fixes, 4 nits. Unique:
  (a) the `_combined_floor` **key-sniffing heuristic** misattributes
  point-floor diagnostics for a *partially* attribution-limited
  transport group, publishing one cell's repeatability numbers under a
  different cell's ID — and the same heuristic is mirrored bug-for-bug
  in `artifact.py`, so validation recomputes the identical wrong answer
  and it ships (`joulewise/analysis_engine/__init__.py:192`
  `_combined_floor`, verified on `main`); (b) `floor_conditions` proxies
  soleness through a **stale field that post-construction mutation does
  not clear** (`joulewise/floor_extraction.py` on `impl/floor-label`);
  (c) **ratio-unit floors publish a J/token claim floor beside
  joule-valued diagnostics**, making the diagnostic read ~150× larger
  than the floor and inverting exactly the relationship the label exists
  to communicate; (d) **no assertion pins the labelled fields on a
  comparative extraction row** — while 80 ABBA members were about to be
  collected against that path. It also flagged that
  `scripts/build_site.py` and `scripts/build_capstone.py` contain
  **zero** references to the new fields (lead-verified on
  `impl/floor-label`: zero hits for `attribution_limited` /
  `floor_label` / `labelled` / `floor_conditions` in both).
- **Sol xhigh independent audit** (fresh, read-only, ~23 min):
  1 blocker + 1 should_fix. Unique: a **runnable probe (V3)**
  demonstrating that the same comparative blocks minted **without**
  admissible half-widths validate clean via `validate_floor_artifact`
  and yield `floor_gate` **5e-324 J** versus **2.6484 J** with widths —
  an artifact that licenses any effect at all. The lead **adjudicated
  this blocker DOWN to registered limitation L1**
  (`docs/decision_log.md` clause 8, confirmation round 9, 2026-07-22 —
  clause header at l.4407, L1 registered at l.4421), which already
  describes exactly this substitution exposure. Sol was a fresh reviewer
  with no knowledge of L1, so **re-finding it was correct reviewer
  behaviour**, and the probe is the **first concrete demonstration** of
  a limitation that had until now been argued only on paper. Recorded
  with the adjudication: FLOOR-LABEL-01 **modestly WIDENS L1's blast
  radius**, because attribution-limited cells that previously refused
  (and were therefore sterile) now publish.
- **Sol xhigh diagnosis** (clock anchor, ~17 min): root cause at **high
  confidence** — transient **wall-clock-versus-monotonic slew exceeding
  the governed 5 ms anchor ceiling**
  (`MAX_WALL_MINUS_MONOTONIC_SPAN_S = 0.005`, gate at
  `joulewise/uncertainty_evidence.py:367`, detail code
  `wall_minus_monotonic_span_exceeded` at l.369): **5.544 ms
  (≈ +110 ppm)** and **7.769 ms (≈ −158 ppm)**. It **corrected the
  lead's hypothesis** by establishing that the failing members' shorter
  duration was a *consequence* of reduction, not a cause. It also
  **correctly refused** to attribute the adjustment to macOS `timed`,
  marking it UNKNOWN because `joulewise/environment.py` assigns
  `limited_without_admin` unconditionally (assignment at l.908, inside
  `_probe_clock_sync` at l.904) — i.e. the field cannot distinguish
  "not synchronising" from "we lack the privilege to see it".
- **Fable adjudication** (21k tokens, **zero tool uses**, 108 s),
  consulted on the lead's own process failure. It **corrected the
  lead's self-diagnosis**: the lead's proposed "act-anyway deadline"
  rule was *not* the right generalization, because with a working wake
  mechanism the information-block would have cost **17 minutes** — the
  10-hour loss is fully explained mechanically, not by a missing
  deadline policy. It then named the underlying disposition: **the lead
  applies rigorous verification to WORK PRODUCTS but exempts its own
  PREMISES ABOUT THE ENVIRONMENT.** Rule set produced: **R1** turn-end
  invariant (end a turn only with the work complete, or with a
  harness-registered wake source named explicitly); **R2**
  quiet-window dominance, with a stop-loss and a heartbeat that checks
  for an in-flight measurement before acting; **R3** premise labeling.
  It identified failure modes the lead's own rules missed — notably
  that **more wakeups can contaminate a live measurement**. It
  recommended **no demotion**, explicitly arguing against its own
  promotion on the grounds that it would operate the same harness with
  the same wake semantics.
- **Lead (Opus 5) bench catches:** detected that its own suite
  verification was **worthless because it piped output through `tail`**,
  which discarded the summary line and masked the real exit code behind
  tail's; **adjudicated Sol's blocker to L1 by reading the primary
  source** rather than accepting the delivered severity; chose **full
  restart over resume** for window C because resuming would mint a
  second pre-calibration and `latest_calibration()` would select it,
  silently breaking the pre/post bracket; **refused to raise
  `--max-failures`** when doing so would have "fixed" the failures by
  accepting corrupted members; and hand-verified that the refactored
  dominance predicate reproduces both prior inline gates for absolute
  and comparative **before either reviewer reported**.

### Lead errors (recorded plainly)

1. **The lost quiet window — the most expensive process error of the
   campaign.** The lead launched the Sol clock diagnosis with
   `nohup … &`, i.e. **outside harness tracking**, and then ended the
   turn "holding until the diagnosis lands". No wake could fire. The
   Mac never slept (`pmset -g log`), and **~10 hours of open quiet
   window were lost** — enough for both remaining collection windows.
   This is the failure Fable's R1/R2 answer.
2. **Over-read run-book §1** to mean the lead must not launch
   measurement windows. Corrected by Ed.
3. **Asserted Ed's session model as fact** while the TUI banner said
   otherwise; `/model` resolved it to Opus 5 (1M). The banner was
   wrong — but the lead's *certainty* was unwarranted either way.
4. **Three failed `codex-run-v3` invocations** from guessing at the
   interface instead of reading the error. The actual cause: the
   literal in-prompt `WRITE_SCOPE:` line must be **valid JSON**.
5. **The FLOOR-LABEL-01 fix round was launched without a sandbox
   flag**, so it defaulted to a **read-only workspace**; `apply_patch`
   was rejected and the session **did no work**. The wrapper still
   **exited 0**, and only the governed report envelope
   (`status: blocked, completion: none`) revealed it.

**Generalization adopted this session (from errors 5 and the `tail`
catch above): EXIT STATUS IS NOT EVIDENCE OF WORK DONE.** Twice in one
session an exit code masked a non-result — a wrapper returning 0 over a
blocked, read-only Sol session, and a test suite whose summary and exit
status were both swallowed by `tail`. The evidence of work done is the
**governed report envelope** (`status` / `completion`) for delegated
runs and the **suite's own summary line** for local runs. Never a shell
exit code, and never a truncated stream. Mirrored into
`docs/process/model_allocation_ledger.md` §6 A-14, because it bears
directly on how delegated work must be verified.

### Collection outcomes

- **Window B** (`04_phase_prefill_abba`): **59/59 members, zero
  failures, zero waivers, zero missing** (lead-verified: 47 campaign
  members + 12 reference-corpus members across
  `runs_window_b_20260726/` and `runs_window_b_20260726_bound/`; every
  `collection.categories` block reports empty `failed` / `missing` /
  `waived`). Pre-calibration **07:04:09Z**, post-calibration
  **10:15:52Z**, `measurement_complete` **10:15:52Z** (lead-reported;
  the two calibration bundles' `sampling_stopped` events are at
  07:03:57Z and 10:15:40Z, ~12 s before each reported stamp —
  consistent, not contradicted). Fresh **NEG-8 dual-family drift bound
  minted in-window**: gross single-member endpoint bound
  **0.750924420078 J**, replicated-endpoint (n=3) bound
  **0.570267900616 J** (verified in
  `runs_window_b_20260726_bound/neg8-drift-bound.json`, fields
  `single_member_endpoint_bound_j` and `replicated_endpoint_bound_j`;
  the lead's dictation called the latter the "triplet mean").
  **The whole-window verdict was still running when this entry was
  written and is recorded as PENDING. No result is asserted here.**
- **Window C** (`05_phase_decode_abba`): **two attempts, both failed on
  the clock slew**, both preserved in custody quarantine. Attempt 1 died
  at **ABBA member 7/40**; attempt 2 at the **dual-family bound mint**,
  which refused member `neg8-refcorpus-r11` (verified: that member's
  `metadata.json` carries `wall_minus_monotonic_span_s` =
  0.007769107818603516 s, and no `neg8-drift-bound.json` was produced in
  `runs_window_c_20260726_bound/`).
- **Window D**: **not started** (`runs_window_d_20260726*` are empty).

### Rough spend (estimates, not billing truth)

Four delegated calls carry figures: the Opus 5 contract lens ~164k
tokens / 50 tool uses / ~11 min; the Fable adjudication 21k tokens /
**zero tool uses** / 108 s; the Sol xhigh independent audit ~23 min and
the Sol xhigh clock diagnosis ~17 min (wall-clock only — per A-11 the
`codex-usage` feed remains unreliable, so no Sol token figures are
recorded). Lead orchestration, the bench catches, and all live
verification on top. Three additional `codex-run-v3` invocations failed
outright on the `WRITE_SCOPE` JSON defect (error 4) and a fourth did no
work under the read-only sandbox default (error 5).

### Verdict and calibration

- **The Opus-contract + Sol-execution pairing gained a second trial**,
  and each lens again found something the other structurally could not:
  the Opus lens traced a *whole labelled path* and found a
  cross-cell **attribution** defect mirrored into the validator (a
  contract-shaped catch, invisible to a probe that only asks "does this
  validate?"), while Sol produced a **runnable artifact-substitution
  probe** with concrete gate numbers (an execution-shaped catch,
  invisible to a reader tracing intended semantics). This is now two
  informal trials — **still not the pre-registered sealed A/B the
  project's own ≥2-trials protocol demands** (see ledger §6 A-8 and
  §5 Q1); the pairing remains the working default on argument, not on
  the project's own evidence standard.
- **Fable as adjudicator of a pre-assembled question is the session's
  strongest allocation datum**: 21k tokens, **zero tool uses**, 108
  seconds, and it **overturned the lead's own conclusion** about the
  lead's own failure, produced a better-shaped rule set than the lead
  had drafted, found failure modes the lead missed, and declined its own
  promotion. The generalizable shape is that the question had already
  been assembled — Fable did no retrieval, only judgment.
- **The auditor-adjudication pattern held again:** a fresh reviewer's
  blocker was correct-as-found and still correctly re-priced by the lead
  against the primary source. Sol's ignorance of L1 was a *feature*
  (independent rediscovery), and the lead reading `decision_log.md`
  rather than accepting the delivered severity is what converted it into
  the right record: **L1 stands, its blast radius is now recorded as
  wider, and it gained its first executable demonstration.**

### Dictated-fact verification notes

This entry was written from lead dictation and verified against primary
evidence. Two dictated line numbers were **off and are corrected above**:
the anchor-ceiling gate is at `joulewise/uncertainty_evidence.py:367`
(dictated `:366`, which is the offset-envelope computation), and the
unconditional `limited_without_admin` assignment is at
`joulewise/environment.py:908` inside `_probe_clock_sync` at l.904
(dictated `:904`). Two dictated facts could **not** be corroborated in
the surviving tree and are recorded as **lead-reported**: the
**5.544 ms** slew instance (no `wall_minus_monotonic_span_s` above
5 ms survives outside `neg8-refcorpus-r11`'s 7.769 ms, consistent with
attempt 1 having been quarantined out of `runs_window_c_20260726/`,
which now holds only its `instrument_validation` bundle), and the exact
window-B calibration stamps (see above). No window-C quarantine
directory was located under the repository root; only
`runs_window_a5_quarantine/` exists from an earlier arc, so the custody
location for the two window-C attempts is **not verified here**.

---

## C-039 addendum: the FIX-6..9 gauntlet, three cold gates, and the 7B floor window (2026-07-29/30)

Continuation of the C-039 index row above, covering the arc that carried
`impl/mint-tool` from `f63a334` to `969a4d6` plus mint #1 and the
`window_7bfloor_20260729` collection. Rulings from this arc are D-083..D-088 (D-088 in the same-day close-out);
the session ledger is the magistrate's own record. Topology: **magistrate**
(Fable, Ed's direct) adjudicating and operating the window solo,
**lieutenant** (Opus 5) directing the Sol pipelines and assembling packets,
**Sol** implementing and auditing, plus the rule-11 **cold gate** (fresh
Fable instance + Opus contract-lens refuter).

### Layers run

| Layer | Instances | Shape |
|---|---|---|
| Sol implementation (enforced `WRITE_SCOPE`) | 4 | FIX-6 `ea20a82`, FIX-7 `7f2c108`, FIX-8 `a14740d`, FIX-9 `969a4d6` |
| Independent audit / delta re-audit | 3+ | FIX-6 delta audit; FIX-8 audit; FIX-9+FIX-8 delta re-audit over `f188562^..969a4d6` |
| Cold gate (cold Fable + paired Opus contract-lens refuter) | 3 | F1 recorded in full (D-087); the pairing is the mechanism, not decoration |
| Magistrate bench verification | continuous | primary-text reads, bit-exact floor recomputation, QA-1 confirmation |
| Modularity survey (Explore agent) | 1 | produced the STACK-ID-BIND-01 lead |

### Unique catches, by layer

- **FIX-9 delta re-audit — blocker QA-1, the arc's decisive catch.**
  Overall verdict **FAIL** (Q1 FAIL, Q2 FAIL, Q3 PASS-WITH-CONCERN, Q4/Q5/Q6
  PASS). QA-1: *"a partial `physical_members` list can launder a
  within-member duplicate into one candidate."* A member declaring
  `bundle_ids: ["x", "x"]` with only one usable `physical_members` row for
  `x` yields a single candidate with identity `(manifest, member_index, -1)`;
  the one-row fast path then accepts its cooldown evidence **without ever
  invoking the supersession matcher**. The `-1` guard prevents a *valid*
  record from matching but does **not** guarantee refusal — a fail-open
  declared-occurrence laundering edge, and a violation of the magistrate's
  default ambiguity-refusal rule. **Magistrate bench-confirmed 2026-07-30.**
  This is the eleventh-plus datum for "fix rounds introduce defects": the
  ruled shape (D-086) was implemented correctly at the hop it named, and the
  defect lives at the *input-shape* boundary the ruling did not reach.
  Also QA-2 (should-fix): no repository fixture composes the real
  supersession validator/reader with the cooldown join — the FIX-9
  regressions stub the reader, which is adequate for join/matcher behavior
  and **insufficient as custody-path closure**.
- **FIX-9 delta re-audit — independent corroboration of the mint.** Q6
  verified the artifact is valid JSON, that its cell and transport-group
  values agree exactly, and that they round to the W6 pins **3.592138**,
  **7.377086**, **7.377086**, with the external statement carrying the same
  formula, roles, source, and no-double-count rule. Independent of the
  magistrate's own bit-exact recomputation (D-084).
- **Cold gate F1 — caught a defect in the magistrate's own packet.** The
  packet asserted `__init__.py` was in no granted `WRITE_SCOPE`; `f63a334`
  (FIX-5) had touched it and introduced the two-site surplus policy, making
  F1 the un-reverted half. The cold layer's value here was **against the
  magistrate**, which is precisely the disposition rule 11 exists to check.
- **Cold gate F1 — C2, the phase-order verification.** The cold instance
  verified from code that `_validate_output_separation` (`__init__.py:85`,
  called at `:1206`) runs **before** inputs load, so the filtered mapping
  does not exist at that point — converting "just filter it" into a
  design-bearing choice and forcing it up to the magistrate rather than
  leaving it to the implementer.
- **Paired Opus contract-lens refuter — narrowed the finding and supplied
  the adopted design.** F1 is **narrower than packeted** (refusal requires a
  surplus entry AND (symlink OR output-containment); no soundness exposure
  either way), and the refuter's **M3 — filter in place, preserve call
  order** beat the magistrate's own two-phase reorder proposal, which was
  **withdrawn**. M2's Opus-verified closed consumer list became a verified
  precondition. Second recorded instance this arc of a paired refuter
  out-designing the adjudicator.
- **Modularity survey (Explore agent) — STACK-ID-BIND-01.** Flagged that
  `analysis_engine/inputs.py:453` reads `artifact.get("sha256")` while
  `mlx_runtime.py:1064-1072` emits `folded_sha256` for directory
  (`file_set`) models — the only shape MLX produces — so
  `floor_stack_identity` returns `None` for real bundles while fixtures use
  the single-file shape and never catch it. CONFIRMED and fixed as FIX-7.
  A survey-shaped layer producing a real claim-side soundness defect.
- **Magistrate bench, B3 referral.** A Sol-vs-Opus **split** on the additive
  effective-clearable-effect reading was **synthesized from primary text, not
  majority-voted**, and resolved NOT-A-DEFECT with the Sol dissent preserved
  (D-083). B1 (device.boundary placeholders) was refuted; the referral
  question — whether the two citations address different objects — was
  answered YES from the clauses' own words.
- **Layer that produced nothing:** the B4 pending-refuter harvest closed
  **empty**. `ref/B4_sol.status` still read RUNNING from the pre-restart
  harness, `ref/B4_sol.md` was never written, and the background job had died
  with the old harness. Pre-assessed superseded / corroboration-only, so the
  disposition was unchanged — but it is recorded here as a **zero-catch
  layer instance** and as a second datum for the standing lesson that a
  background job which cannot wake its parent is a job that did not run.

### Window operation

`window_7bfloor_20260729` was operated by the magistrate **solo** (D-085):
quiet-lock covers all agent sessions, and a solo operator avoids the known
grandchild-notification misroute. Interaction was at stage boundaries only,
with zero tool calls during stages. The window completed **PASSED** and
claim-bearing on basis `3ff9128b…f1173`, through **two live contamination
events** (macOS's malware scanner, then a second, unidentified CPU
excursion — the operator log records only an hourly-snapshot *hypothesis*
for it) that the admission gates caught and that the protocol recovered from per its own written
playbook — the first arc in which the recovery path was exercised rather
than theorised. The **third-failure-closes** rule was ratified as cold-gate
precedent during this operation (D-087).

### Process observations

- **The escalation trigger armed and was honoured.** C3 armed the standing
  same-signature trigger before FIX-8 ran; the arc did not need to fire it
  for that signature. FIX-9 is a *different* defect at a different hop, not
  round three on the same one.
- **The cold-gate mechanism earned its cost this arc**: three exercises, one
  packet correction against the magistrate, one design substitution adopted
  over the magistrate's proposal, one code-verified precondition. Retain.
- **Open at the addendum's writing:** QA-1 is an unclosed blocker on
  `impl/mint-tool`; the merge train is gated on its disposition. QA-2, F2,
  F3, and Audit-F1 are registered in the 2026-07-30 queue intake batch.

### Addendum close-out (2026-07-30, later the same day)

The "open at the addendum's writing" state above resolved as follows. FIX-10
(Sol high, magistrate bench-reviewed, `16c7af0`) closed QA-1 with
declared-occurrence tallying and the real validator/reader/join fixture;
its own delta re-audit (Sol xhigh) then **FAILED with two successor
blockers** (QA-10A map-omission, QA-10B existing-retry laundering) — the
second consecutive same-signature fix-round failure. The standing escalation
trigger FIRED and was honoured: no FIX-11 was ordered; a mandatory cold gate
(fresh Fable + Opus contract-lens refuter, exercise #4 of the pairing) ruled
and the magistrate synthesized D-088 — join hardening moved to its own
gauntlet under a ratified contract; the branch merge licensed at the audited
head with the blockers registered.

Layer catches this round: the **delta re-audit layer** caught both successor
blockers a green 2280-test suite could not see (the fixtures were all
hardcoded `invoked`); the **refuter layer** caught that FIX-10 was conformant
with ruling R2 and the *ruling* was the QA-10B defect (a finding against the
magistrate, on the record in D-088 cl.6), plus the declaration-order
discriminator the cold instance's contract had missed; the **cold-gate
layer** caught the structural cause (the missing existing-outcome bit) that
both fix-round formulations had danced around, and the QA-10A escape path
through `floor_extraction`'s map-iteration completeness. Three independent
corpus scans (magistrate, cold instance, refuter) each verified both blocker
shapes absent from all claim-bearing evidence.

---

## C-039 addendum II: two escalation consults — the cooldown-join design consult and the contrast-window recovery (2026-07-30/31)

Second continuation of the C-039 index row. Both entries here are **consults
convened because an escalation trigger fired**, not council rounds convened by
ritual — one on a code defect class, one live inside a measurement window. The
rulings are D-089 (join) and the window's own §10 continuation record.

### (i) Cooldown-join design consult → D5-J (2026-07-30)

**Trigger.** The FIX-10 independent audit returned FAIL on B1 (coverage
checked against emissions rather than declarations, so a partial supersession
launders a declared-but-malformed occurrence) and B2 (filtered sibling
manifests never contribute declarations) — the **third consecutive round
leaving a residual of the same signature**. Per hard rule 11 the next spend was
a **design consult, not a fix round**; the merge train was held pending its
disposition.

**Layer:** Sol xhigh design consult, thread `019fb5c8…3937`,
codex-adjudicated with lead replays, question scoped to *where
declaration-completeness is enforced* (the ONE home).

**Unique catches:**

- **The consult reframed the defect class out of existence rather than
  patching its third instance.** D5-J moves the matcher contract
  observed→declared, which kills B1 *structurally*; catalog-completeness gate
  C answers B2 without a blanket directory-hygiene rule; the `-1` sentinel
  retires because declarations carry true positions. Three fix rounds had each
  patched a coverage site; the consult found there should be one owner.
- **A 23-cell truth table, of which the consult itself flagged one cell as a
  judgment call** — `(|D| ≥ 2, E ⊂ D, exact record naming all of D,
  selected ∈ E)` — and offered a collapse alternative rather than deciding it.
  The magistrate **STRUCK** the cell (uniform malformation ⇒ refuse;
  near-unreachable in any case; the cost of refusing is the standard
  repair-or-re-collect path), leaving **exactly two accepting shapes**. A
  consult that hands its adjudicator the one cell it should not decide alone
  is the behaviour the pre-decision-consult rule is buying.
- **Interim-merge answer NO.** The lead's own preference was a conservative
  interim guard (D1) that would license the merge now; the consult established
  D1 cannot cover B2, so the structural fix lands pre-merge. Second recorded
  instance this arc of the consulted layer beating the adjudicator's proposal.

Real-corpus behaviour is unchanged either way (**57/57, both supersessions
consumed**) — the blockers are adversarial-shaped and need corrupted custody
inputs. Implementation is FIX-11 in name, **structural in kind and
consult-sanctioned**, queued behind the metrology campaign authoring in the
same worktree. [RESOLVED 2026-07-31: implemented first (the authoring Sol
session had died), merged via PR #89 under the D-093 cold-gate synthesis;
metrology authoring relaunched after the merge on `impl/metrology-campaigns`.]

### (ii) Contrast-window recovery consult (2026-07-31, live in-window)

**Trigger.** Two consecutive same-signature failures of the start-triplet r1
slot on CPU admission (`cpu_busy_ratio_p95` 0.726 against a 0.5 gate), the
second after a relaunch premised on a **misattributed** cause — the operator
verified Time Machine was clear but did not verify overall CPU quiet, and the
true cause (an XProtect Remediator sweep) was still running. The standing
same-signature trigger fired; per rule 11 the next spend was a consult, not a
third blind relaunch.

**Layer:** bounded Sol xhigh consult, thread `019fb69a-7692`, convened by the
solo window operator between stages.

**Unique catches:**

- **The one-invocation supersession contract.** The consult established that
  the supersession recorder must be run **exactly once, post-window**, naming
  the selected occurrence and both superseded ones together. The operator's
  in-flight plan would have recorded per failure — **double-recording, which
  voids campaign membership downstream** (the recorder's silent
  duplicate-append defect, `SUPERSESSION-DUP-REFUSAL-01`). This is the catch
  that saved the window's claim-bearing status: the collection would have
  passed and the custody record would have been unusable.
- **The wait criterion: full sweep, not just the observed module.** The
  operator's instinct was to wait out `XProtectRemediatorPirrit`, the module
  actually observed at 941 CPU ms/s. The consult's criterion was the **entire
  remediator sweep** — modules run sequentially, so clearing one says nothing
  about the next. The sweep ran to 05:31Z; a second, unrelated intruder
  (`corespotlightd` at 624 CPU ms/s, Spotlight indexing the fresh bundles) was
  then also waited out, and round 3 launched only after a full-sweep
  completion, **eight consecutive daemon-quiet minutes past the Time Machine
  hour boundary**, and a clean final `powermetrics` tasks sample.
- **Continuation chain-shape verification.** The consult verified the round-3
  continuation was §10-shaped: it pins the window's original pre-calibration
  and re-runs the §5B screen, so the recovery does not silently re-baseline
  the window.

**Outcome:** round 3 ran the entire window **without a single further
admission event** — 40/40 science members usable, zero science-member
failures, whole-window verdict PASSED. The supersession was recorded once,
post-window, per the consult-verified contract. The window used 2 of its 3
permitted failures, both on one reference slot; the third-failure-closes
salvage rule (D-087) was never invoked.

**Process note.** This is the first recorded instance of the standing
escalation trigger firing **inside a measurement window** rather than over a
code defect, and of a consult being convened at a stage boundary by a solo
operator under quiet-lock. The cost was one consult against a ~2.6-hour window
that would otherwise have been re-run on a third guess; the mechanism should be
retained for window operation, not just for fix rounds.

## C-039 addendum III: the clock-anchor knife-edge consult (2026-08-01, in-window)

**Trigger.** Metrology window B's launch 1 aborted at the §5B
pre-calibration gate twice with the same signature
(`clock_anchor_unresolved` / `native_intersection_empty`) — and the
signature matched window A's post-cal attempt-1 failure from the prior
night. Three same-signature calibration failures across two windows is
exactly the standing escalation trigger's shape; per rule 11 the next
spend was a consult, not a third blind launch.

**Layer:** bounded Sol xhigh consult, read-only, one round, convened by
the solo window operator between launches (~01:00–01:30 PT). Full memo:
session scratchpad `693609a9…/scratchpad/consult_anchor_v2.md`; findings
ratified into D-099.

**Unique catches:**

- **The anchor is knife-edge by construction, and the lead's mechanism
  was wrong.** The operator's working theory was cadence drift in the
  capture stream. The consult showed the theory was
  quantization-confounded and replaced it: at 197 s capture length the
  native-second intersection margins were +0.86/+1.41 ms on the passing
  attempts vs −0.25/−0.26/−0.51 ms on the failures, while the
  *unmodeled* controller wall/monotonic rate (~−12 ppm ≈ 2.3 ms per
  capture) exceeds every margin — pass/fail at this capture length is
  quantization-phase luck, an instrument-design finding (rate-aware
  anchor mapping is the queued repair) rather than an environmental
  fault to wait out.
- **Time Machine exonerated, and the prep-script proxy with it.**
  `tmutil destinationinfo` showed no destinations configured; the prep
  script's "TM RUNNING" line detects process residency only. This
  retroactively taints window A's failure-#3 "TM-consistent"
  attribution and re-identifies the overnight intruder class as
  mobileassetd/softwareupdated (~04:29 PT both nights) plus bird.
- **Discipline on the causal claim.** The consult recorded bird (99%
  CPU uploading the prior window's 10.4 GB backup) as *plausible
  trigger and objective preflight violation* — explicitly NOT confirmed
  root cause. The distinction is what kept the relaunch decision
  honest: launch 2 proceeded under a hardened protocol (bird-SIGSTOP
  with identity custody and a fail-safe CONT trap) plus a predeclared
  budget (frozen chain unchanged, built-in retry pair only, night
  closes if the gate aborts again), rather than on a claimed fix.

**Outcome:** launch 2 passed pre-calibration on the first attempt
(b_fiducial 0.032787 s) and the window collected its core payload
through to a clean salvage close. The consult cost one bounded session
against an 11-hour runway that two more blind aborts would have burned.

**Process note.** Second recorded instance of the escalation trigger
firing inside a measurement window (first: C-039 addendum II (ii)), and
the first where the consult *refuted the lead's mechanism* while
confirming the lead's decision shape. The pattern holding across both:
the consult's unique value is causal discipline under time pressure —
separating "what we can prove" from "what we are tempted to conclude"
before the next launch is committed.
## C-040: The commit-3 gauntlet — five fix rounds, two cold gates, and what each layer uniquely caught (2026-08-01/02)

**Shape.** Composed commit (Sol xhigh, ratified design) → independent
delta audit → fix rounds each followed by a FRESH-thread re-audit →
rule-11 cold gates when triggers fired (twice) → [outcome line filled at
close]. All delegated; magistrate gates: suite + mapping-hash pins at
every head, bench verification of every load-bearing audit claim before
acting.

**Per-layer unique catches (zero dead layers this arc):**
- Implementer self-verification: caught nothing the auditors later
  confirmed as remaining — necessary but NEVER sufficient, again.
- Audit 1: crash-strand ordering, v1-pinned verdict verifier (a DESIGN
  scope omission it attributed as implementation), path normalization.
- Re-audit 1 (fresh): proved fix-1's heal unreachable-shaped and the
  same-signature persistence that fired the trigger.
- COLD GATE 1 — cold instance: THE ROOT CAUSE (the design's
  attest-after-publish clause guarantees the crash window; both prior
  rounds were downstream patches). Refuter: the design's TWO
  contradictory acceptance clauses; the pointwise-vs-enumerative
  aggregation distinction that OVERTURNED the cold instance's B2 order
  (magistrate overruled with dissent, bench-verified); the torn-log-line
  second brick + its v1-history regression that the re-audit had called
  acceptable; the B2 trigger miscount (round 1 had no license).
- Re-audit 2: three narrow adjacencies in an otherwise-passing
  structural implementation (fail-open lock surfaces, tolerance
  breadth, test fidelity).
- Re-audit 3: unbound lock token; enumeration-shaped tail (the pattern
  recurrence that fired the second gate).
- COLD GATE 2 (convergent): both instances independently probed
  CPython's json taxonomy and rejected BOTH magistrate candidates.
  Refuter uniquely: the whitespace-preservation hole (json.loads
  tolerates trailing whitespace → permanent acceptance of
  writer-impossible bytes) that had survived FOUR prior reviews; the
  packet's miscited B3/NUL precedent. Cold instance uniquely: the
  '{"a": 1e' false-refusal proving pos-based refinements unsound; the
  byte-exact canonical round-trip construction.
- Re-audit 4: token aliasing across release/reacquire (bare-Path
  registry keys); two recognizer grammar corners (canonical key
  ordering; -0.0); single-fd TOCTOU; exception-path cleanup.

**Process findings for the skills:**
1. Fix rounds introduce defects — now proven FIVE consecutive times on
   one commit; the fresh-thread re-audit after EVERY round is
   non-negotiable doctrine, permanently.
2. The refuter layer's value concentrates exactly where instances agree
   too readily: both its overturning arguments (B2 aggregation; the
   whitespace hole) came with runnable probes, not rhetoric. Keep
   requiring probes in refuter briefs.
3. Formulation-vs-implementation trigger parsing is a loophole risk:
   the D-104 disposition note's pattern (one explicit fidelity round,
   then ANY blocker → gate + descope, no further parsing) is the
   containment shape to reuse.
4. Directing-subagent stalls (4×) and the MCP 1800 s timeout: audited
   CLI route for >30 min Sol rounds; harvest-from-disk + process
   watchdogs as standing practice (memory recorded).
5. Magistrate candidate formulations in cold-gate packets get REJECTED
   when drafted at the bench under fatigue (both round-4 candidates) —
   the gate caught both; drafting candidates is still net-positive
   (they focus the ruling) but they must be labelled candidates, never
   presumptive.

**COLD GATE 3 (disposition, 2026-08-02) addendum:**
- Round 5 closed the lock mechanism entirely (all identity attacks
  incl. field-copied clones) but left two recognizer-exactness
  blockers; the binding commitment fired as written — no round 6.
- Cold instance: Option A on the merits with verbatim fences + complete
  closure procedures; its own wider absence scan (40 files vs the
  packet's 33 — depth-1 glob error caught); demanded the third
  independent scan and made lead live verification an explicit merge
  condition rather than trusting the packet's uncited green claim.
- Refuter (the arc's strongest document): did NOT oppose landing;
  replaced the fences — the preserve-then-truncate custody sidecar
  (classifier errors can no longer destroy evidence, decoupling
  exactness from custody), the 2-line writer-side ASCII key assertion
  (closed five unvalidated splice sites nobody had seen), proof the
  ratified R7 pin was implemented over a synthetic corpus and missed
  F1 by ONE character position, proof the number-grammar's literal
  subset direction is undecidable-at-sane-cost (three rounds failed on
  it), the branch-introduced-vs-pre-existing precedent distinction,
  and the packet-hygiene finding (runway/cost-of-delay context reached
  a cold instance — recorded as a process rule: sealed annex only).
- Synthesis D-105: land via custody micro-commit + narrow audit;
  registration as a NEW ruling; exactness struck for a documented
  decidable superset; D-104 cl.2 amended.
- Layer scorecard update: the refuter layer has now overturned or
  materially amended the magistrate/cold-instance position at ALL THREE
  gates — it is the single highest-unique-catch layer of the project
  and its probe-required brief format is ratified practice.

**Outcome.** Gauntlet commit 3 MERGED as PR #93 (`cb860e1`, 2026-08-02):
composed commit + five audited fix rounds + custody micro-commit +
bench fixes + the frozen exact-set pin; suite 2352 OK at the final
head; 57/57 + 47/47 mapping pins hash-identical at every head of the
branch; COOLDOWN-JOIN-GAUNTLET-01 and QA-10A/QA-10B retired; the D-088
standing conditions and D-093 scans lifted per their row contracts;
residual exactness blockers registered non-downgradable in
C3-RECOGNIZER-EXACT-01 under D-105's compensating controls (custody
sidecar; writer-side key assertion). Total spend: ~6 Sol implementation
sessions, 6 independent audits, 3 cold-gate pairs, across ~20 hours of
the Ed-authorized runway — the most heavily reviewed change in the
project's history, protecting the machinery every future claim
consumes.

## C-040 addendum: the b-ii cold gate (D-106), the merge-fallback landings, and the codex envelope bug (2026-08-02/03)

**Shape.** The runway's second half ran both repair branches through
brief-repair rounds to decisive re-audits: MANIFEST-CONTRAST v3 came
back CLEAN (zero findings) and merged as PR #95; MET-DANGLER's decisive
re-audit left ONE blocker (B3-R1), the disposition note's binding
commitment fired as written — no third formulation round — and the
question went to the runway's FOURTH cold gate (cold Fable + Opus
contract refuter), synthesized as **D-106 Variant D**. Full packet and
re-audit custody: `.desk/coldgate_d100_bii/`.

**Per-layer unique catches (no dead layers):**
- Decisive re-audit (Sol xhigh, fresh thread): B3-R1 itself — after two
  formulation rounds, telemetry and nested content remained unbound to
  the admission-only event account (earlier-capture substitution
  licensed; negative time deltas accepted; nested `model_output`
  unrecognized-and-passing). Also re-proved all five regressions red on
  the parent by code inspection, under a code-inspection-only ruling.
- Cold instance: Option A + window-B YES on the compensating-control
  theory; its own stated strongest counterargument (doctrinal fences
  decay) converged with the refuter's B-1 — recorded as dissent when
  overruled.
- Refuter (Opus, contract lens): the gate's decisive layer for the
  FOURTH consecutive time, all showings bench-verified — the recorded
  manual verification contains ZERO bundle digests, so Option A's fence
  binds by path against a content-substitution defect; the packet's
  condition-3 parenthetical quoted only the half supporting the
  magistrate's lean; the window's three sibling quarantine bundles are
  mutually substitutable by one same-name copy, defeating the
  rider-(ii) exemption; the NEW writer-level fact (powermetrics emits
  identity-free 8-field rows from one code path, so per-file schema
  formulations can NEVER bind capture identity) that diagnosed both
  failed formulations and discriminated the fix in kind; and S-1 — the
  D-105 registration guard inverted on first contact (it registered
  the undecidable; this residual is decidable), so NOTHING is
  registered.
- Magistrate: Variant D synthesis; two packet-hygiene failures recorded
  against itself (the Option C runway line; the selective quotation);
  cold-gate packet authorship moved to MECHANICAL assembly permanently.

**The merge-fallback pattern (twice, ruled):** GitHub could not build or
schedule merge-ref CI for PR #94 (pull_request runs never scheduled;
close/reopen tried) or PR #95. Ruled fallback, both times: satisfy
D-072's substance far past precedent (three independent audits + cold
gate + lead full suite at the audited head + hash-identical mapping
pins; for #95, the composed-tree full suite as the lead integration
gate), merge, and treat the push-to-main verdict CI as the verdict with
immediate revert on red. Both verdict runs came back green.

**Site failure domain (D-101 addenda I+II):** the D-106 decision-log
commit itself turned main red through the live-content site pack tests
— a governed record edit acting as a session blocker, which D-101
forbids in substance. The defect was fixed on its merits (anchor
minting), the CLASS closed by Ed's directive (live-content site tests
advisory-lane, addendum I), and the site observatory then split into
its own workflow and failure domain (addendum II; separate `site`
workflow 2/2 green).

**Process finding — the codex envelope bug:** both of the runway's
final xhigh runs (the D100-BII implementation; the TEST-SPEED consult)
completed their work but lost the final envelope — protocol failure by
contract, so the implementation diff was HELD untrusted on its pushed
branch. Root cause (found 2026-08-03): a codex CLI models-cache schema
drift — cached entries lacked `supports_reasoning_summaries` and the
TTL-renewal deserialization killed sessions before the final message.
FIXED 2026-08-02 evening (stale cache moved aside, fresh refetch
carries the field, trivial Sol run verified end-to-end). The
held-untrusted → independent-focused-audit disposition worked exactly
as the bridge contract intends: no envelope, no trust, regardless of
how green the work looked.

**Outcome.** PRs #94 and #95 MERGED at audited heads with green verdict
runs; D100-BII-BINDING-01 minted (P1) carrying D-106 clause 3's four
parts; window B re-evaluation hard-blocked on it; its focused
independent audit launched 2026-08-02 evening (successor session) with
the repaired codex path. Layer scorecard: the probe-required refuter
brief format remains the project's highest-unique-catch instrument —
four gates, four material amendments or overrulings.


exec
/bin/zsh -lc "sed -n '2118,2260p' docs/council_log.md; sed -n '2260,2415p' docs/council_log.md" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
## C-039 addendum: the FIX-6..9 gauntlet, three cold gates, and the 7B floor window (2026-07-29/30)

Continuation of the C-039 index row above, covering the arc that carried
`impl/mint-tool` from `f63a334` to `969a4d6` plus mint #1 and the
`window_7bfloor_20260729` collection. Rulings from this arc are D-083..D-088 (D-088 in the same-day close-out);
the session ledger is the magistrate's own record. Topology: **magistrate**
(Fable, Ed's direct) adjudicating and operating the window solo,
**lieutenant** (Opus 5) directing the Sol pipelines and assembling packets,
**Sol** implementing and auditing, plus the rule-11 **cold gate** (fresh
Fable instance + Opus contract-lens refuter).

### Layers run

| Layer | Instances | Shape |
|---|---|---|
| Sol implementation (enforced `WRITE_SCOPE`) | 4 | FIX-6 `ea20a82`, FIX-7 `7f2c108`, FIX-8 `a14740d`, FIX-9 `969a4d6` |
| Independent audit / delta re-audit | 3+ | FIX-6 delta audit; FIX-8 audit; FIX-9+FIX-8 delta re-audit over `f188562^..969a4d6` |
| Cold gate (cold Fable + paired Opus contract-lens refuter) | 3 | F1 recorded in full (D-087); the pairing is the mechanism, not decoration |
| Magistrate bench verification | continuous | primary-text reads, bit-exact floor recomputation, QA-1 confirmation |
| Modularity survey (Explore agent) | 1 | produced the STACK-ID-BIND-01 lead |

### Unique catches, by layer

- **FIX-9 delta re-audit — blocker QA-1, the arc's decisive catch.**
  Overall verdict **FAIL** (Q1 FAIL, Q2 FAIL, Q3 PASS-WITH-CONCERN, Q4/Q5/Q6
  PASS). QA-1: *"a partial `physical_members` list can launder a
  within-member duplicate into one candidate."* A member declaring
  `bundle_ids: ["x", "x"]` with only one usable `physical_members` row for
  `x` yields a single candidate with identity `(manifest, member_index, -1)`;
  the one-row fast path then accepts its cooldown evidence **without ever
  invoking the supersession matcher**. The `-1` guard prevents a *valid*
  record from matching but does **not** guarantee refusal — a fail-open
  declared-occurrence laundering edge, and a violation of the magistrate's
  default ambiguity-refusal rule. **Magistrate bench-confirmed 2026-07-30.**
  This is the eleventh-plus datum for "fix rounds introduce defects": the
  ruled shape (D-086) was implemented correctly at the hop it named, and the
  defect lives at the *input-shape* boundary the ruling did not reach.
  Also QA-2 (should-fix): no repository fixture composes the real
  supersession validator/reader with the cooldown join — the FIX-9
  regressions stub the reader, which is adequate for join/matcher behavior
  and **insufficient as custody-path closure**.
- **FIX-9 delta re-audit — independent corroboration of the mint.** Q6
  verified the artifact is valid JSON, that its cell and transport-group
  values agree exactly, and that they round to the W6 pins **3.592138**,
  **7.377086**, **7.377086**, with the external statement carrying the same
  formula, roles, source, and no-double-count rule. Independent of the
  magistrate's own bit-exact recomputation (D-084).
- **Cold gate F1 — caught a defect in the magistrate's own packet.** The
  packet asserted `__init__.py` was in no granted `WRITE_SCOPE`; `f63a334`
  (FIX-5) had touched it and introduced the two-site surplus policy, making
  F1 the un-reverted half. The cold layer's value here was **against the
  magistrate**, which is precisely the disposition rule 11 exists to check.
- **Cold gate F1 — C2, the phase-order verification.** The cold instance
  verified from code that `_validate_output_separation` (`__init__.py:85`,
  called at `:1206`) runs **before** inputs load, so the filtered mapping
  does not exist at that point — converting "just filter it" into a
  design-bearing choice and forcing it up to the magistrate rather than
  leaving it to the implementer.
- **Paired Opus contract-lens refuter — narrowed the finding and supplied
  the adopted design.** F1 is **narrower than packeted** (refusal requires a
  surplus entry AND (symlink OR output-containment); no soundness exposure
  either way), and the refuter's **M3 — filter in place, preserve call
  order** beat the magistrate's own two-phase reorder proposal, which was
  **withdrawn**. M2's Opus-verified closed consumer list became a verified
  precondition. Second recorded instance this arc of a paired refuter
  out-designing the adjudicator.
- **Modularity survey (Explore agent) — STACK-ID-BIND-01.** Flagged that
  `analysis_engine/inputs.py:453` reads `artifact.get("sha256")` while
  `mlx_runtime.py:1064-1072` emits `folded_sha256` for directory
  (`file_set`) models — the only shape MLX produces — so
  `floor_stack_identity` returns `None` for real bundles while fixtures use
  the single-file shape and never catch it. CONFIRMED and fixed as FIX-7.
  A survey-shaped layer producing a real claim-side soundness defect.
- **Magistrate bench, B3 referral.** A Sol-vs-Opus **split** on the additive
  effective-clearable-effect reading was **synthesized from primary text, not
  majority-voted**, and resolved NOT-A-DEFECT with the Sol dissent preserved
  (D-083). B1 (device.boundary placeholders) was refuted; the referral
  question — whether the two citations address different objects — was
  answered YES from the clauses' own words.
- **Layer that produced nothing:** the B4 pending-refuter harvest closed
  **empty**. `ref/B4_sol.status` still read RUNNING from the pre-restart
  harness, `ref/B4_sol.md` was never written, and the background job had died
  with the old harness. Pre-assessed superseded / corroboration-only, so the
  disposition was unchanged — but it is recorded here as a **zero-catch
  layer instance** and as a second datum for the standing lesson that a
  background job which cannot wake its parent is a job that did not run.

### Window operation

`window_7bfloor_20260729` was operated by the magistrate **solo** (D-085):
quiet-lock covers all agent sessions, and a solo operator avoids the known
grandchild-notification misroute. Interaction was at stage boundaries only,
with zero tool calls during stages. The window completed **PASSED** and
claim-bearing on basis `3ff9128b…f1173`, through **two live contamination
events** (macOS's malware scanner, then a second, unidentified CPU
excursion — the operator log records only an hourly-snapshot *hypothesis*
for it) that the admission gates caught and that the protocol recovered from per its own written
playbook — the first arc in which the recovery path was exercised rather
than theorised. The **third-failure-closes** rule was ratified as cold-gate
precedent during this operation (D-087).

### Process observations

- **The escalation trigger armed and was honoured.** C3 armed the standing
  same-signature trigger before FIX-8 ran; the arc did not need to fire it
  for that signature. FIX-9 is a *different* defect at a different hop, not
  round three on the same one.
- **The cold-gate mechanism earned its cost this arc**: three exercises, one
  packet correction against the magistrate, one design substitution adopted
  over the magistrate's proposal, one code-verified precondition. Retain.
- **Open at the addendum's writing:** QA-1 is an unclosed blocker on
  `impl/mint-tool`; the merge train is gated on its disposition. QA-2, F2,
  F3, and Audit-F1 are registered in the 2026-07-30 queue intake batch.

### Addendum close-out (2026-07-30, later the same day)

The "open at the addendum's writing" state above resolved as follows. FIX-10
(Sol high, magistrate bench-reviewed, `16c7af0`) closed QA-1 with
declared-occurrence tallying and the real validator/reader/join fixture;
its own delta re-audit (Sol xhigh) then **FAILED with two successor
blockers** (QA-10A map-omission, QA-10B existing-retry laundering) — the
second consecutive same-signature fix-round failure. The standing escalation
trigger FIRED and was honoured: no FIX-11 was ordered; a mandatory cold gate
(fresh Fable + Opus contract-lens refuter, exercise #4 of the pairing) ruled
and the magistrate synthesized D-088 — join hardening moved to its own
gauntlet under a ratified contract; the branch merge licensed at the audited
head with the blockers registered.

Layer catches this round: the **delta re-audit layer** caught both successor
blockers a green 2280-test suite could not see (the fixtures were all
hardcoded `invoked`); the **refuter layer** caught that FIX-10 was conformant
with ruling R2 and the *ruling* was the QA-10B defect (a finding against the
magistrate, on the record in D-088 cl.6), plus the declaration-order
discriminator the cold instance's contract had missed; the **cold-gate
layer** caught the structural cause (the missing existing-outcome bit) that
both fix-round formulations had danced around, and the QA-10A escape path
through `floor_extraction`'s map-iteration completeness. Three independent
corpus scans (magistrate, cold instance, refuter) each verified both blocker
shapes absent from all claim-bearing evidence.

---

## C-039 addendum II: two escalation consults — the cooldown-join design consult and the contrast-window recovery (2026-07-30/31)
## C-039 addendum II: two escalation consults — the cooldown-join design consult and the contrast-window recovery (2026-07-30/31)

Second continuation of the C-039 index row. Both entries here are **consults
convened because an escalation trigger fired**, not council rounds convened by
ritual — one on a code defect class, one live inside a measurement window. The
rulings are D-089 (join) and the window's own §10 continuation record.

### (i) Cooldown-join design consult → D5-J (2026-07-30)

**Trigger.** The FIX-10 independent audit returned FAIL on B1 (coverage
checked against emissions rather than declarations, so a partial supersession
launders a declared-but-malformed occurrence) and B2 (filtered sibling
manifests never contribute declarations) — the **third consecutive round
leaving a residual of the same signature**. Per hard rule 11 the next spend was
a **design consult, not a fix round**; the merge train was held pending its
disposition.

**Layer:** Sol xhigh design consult, thread `019fb5c8…3937`,
codex-adjudicated with lead replays, question scoped to *where
declaration-completeness is enforced* (the ONE home).

**Unique catches:**

- **The consult reframed the defect class out of existence rather than
  patching its third instance.** D5-J moves the matcher contract
  observed→declared, which kills B1 *structurally*; catalog-completeness gate
  C answers B2 without a blanket directory-hygiene rule; the `-1` sentinel
  retires because declarations carry true positions. Three fix rounds had each
  patched a coverage site; the consult found there should be one owner.
- **A 23-cell truth table, of which the consult itself flagged one cell as a
  judgment call** — `(|D| ≥ 2, E ⊂ D, exact record naming all of D,
  selected ∈ E)` — and offered a collapse alternative rather than deciding it.
  The magistrate **STRUCK** the cell (uniform malformation ⇒ refuse;
  near-unreachable in any case; the cost of refusing is the standard
  repair-or-re-collect path), leaving **exactly two accepting shapes**. A
  consult that hands its adjudicator the one cell it should not decide alone
  is the behaviour the pre-decision-consult rule is buying.
- **Interim-merge answer NO.** The lead's own preference was a conservative
  interim guard (D1) that would license the merge now; the consult established
  D1 cannot cover B2, so the structural fix lands pre-merge. Second recorded
  instance this arc of the consulted layer beating the adjudicator's proposal.

Real-corpus behaviour is unchanged either way (**57/57, both supersessions
consumed**) — the blockers are adversarial-shaped and need corrupted custody
inputs. Implementation is FIX-11 in name, **structural in kind and
consult-sanctioned**, queued behind the metrology campaign authoring in the
same worktree. [RESOLVED 2026-07-31: implemented first (the authoring Sol
session had died), merged via PR #89 under the D-093 cold-gate synthesis;
metrology authoring relaunched after the merge on `impl/metrology-campaigns`.]

### (ii) Contrast-window recovery consult (2026-07-31, live in-window)

**Trigger.** Two consecutive same-signature failures of the start-triplet r1
slot on CPU admission (`cpu_busy_ratio_p95` 0.726 against a 0.5 gate), the
second after a relaunch premised on a **misattributed** cause — the operator
verified Time Machine was clear but did not verify overall CPU quiet, and the
true cause (an XProtect Remediator sweep) was still running. The standing
same-signature trigger fired; per rule 11 the next spend was a consult, not a
third blind relaunch.

**Layer:** bounded Sol xhigh consult, thread `019fb69a-7692`, convened by the
solo window operator between stages.

**Unique catches:**

- **The one-invocation supersession contract.** The consult established that
  the supersession recorder must be run **exactly once, post-window**, naming
  the selected occurrence and both superseded ones together. The operator's
  in-flight plan would have recorded per failure — **double-recording, which
  voids campaign membership downstream** (the recorder's silent
  duplicate-append defect, `SUPERSESSION-DUP-REFUSAL-01`). This is the catch
  that saved the window's claim-bearing status: the collection would have
  passed and the custody record would have been unusable.
- **The wait criterion: full sweep, not just the observed module.** The
  operator's instinct was to wait out `XProtectRemediatorPirrit`, the module
  actually observed at 941 CPU ms/s. The consult's criterion was the **entire
  remediator sweep** — modules run sequentially, so clearing one says nothing
  about the next. The sweep ran to 05:31Z; a second, unrelated intruder
  (`corespotlightd` at 624 CPU ms/s, Spotlight indexing the fresh bundles) was
  then also waited out, and round 3 launched only after a full-sweep
  completion, **eight consecutive daemon-quiet minutes past the Time Machine
  hour boundary**, and a clean final `powermetrics` tasks sample.
- **Continuation chain-shape verification.** The consult verified the round-3
  continuation was §10-shaped: it pins the window's original pre-calibration
  and re-runs the §5B screen, so the recovery does not silently re-baseline
  the window.

**Outcome:** round 3 ran the entire window **without a single further
admission event** — 40/40 science members usable, zero science-member
failures, whole-window verdict PASSED. The supersession was recorded once,
post-window, per the consult-verified contract. The window used 2 of its 3
permitted failures, both on one reference slot; the third-failure-closes
salvage rule (D-087) was never invoked.

**Process note.** This is the first recorded instance of the standing
escalation trigger firing **inside a measurement window** rather than over a
code defect, and of a consult being convened at a stage boundary by a solo
operator under quiet-lock. The cost was one consult against a ~2.6-hour window
that would otherwise have been re-run on a third guess; the mechanism should be
retained for window operation, not just for fix rounds.

## C-039 addendum III: the clock-anchor knife-edge consult (2026-08-01, in-window)

**Trigger.** Metrology window B's launch 1 aborted at the §5B
pre-calibration gate twice with the same signature
(`clock_anchor_unresolved` / `native_intersection_empty`) — and the
signature matched window A's post-cal attempt-1 failure from the prior
night. Three same-signature calibration failures across two windows is
exactly the standing escalation trigger's shape; per rule 11 the next
spend was a consult, not a third blind launch.

**Layer:** bounded Sol xhigh consult, read-only, one round, convened by
the solo window operator between launches (~01:00–01:30 PT). Full memo:
session scratchpad `693609a9…/scratchpad/consult_anchor_v2.md`; findings
ratified into D-099.

**Unique catches:**

- **The anchor is knife-edge by construction, and the lead's mechanism
  was wrong.** The operator's working theory was cadence drift in the
  capture stream. The consult showed the theory was
  quantization-confounded and replaced it: at 197 s capture length the
  native-second intersection margins were +0.86/+1.41 ms on the passing
  attempts vs −0.25/−0.26/−0.51 ms on the failures, while the
  *unmodeled* controller wall/monotonic rate (~−12 ppm ≈ 2.3 ms per
  capture) exceeds every margin — pass/fail at this capture length is
  quantization-phase luck, an instrument-design finding (rate-aware
  anchor mapping is the queued repair) rather than an environmental
  fault to wait out.
- **Time Machine exonerated, and the prep-script proxy with it.**
  `tmutil destinationinfo` showed no destinations configured; the prep
  script's "TM RUNNING" line detects process residency only. This
  retroactively taints window A's failure-#3 "TM-consistent"
  attribution and re-identifies the overnight intruder class as
  mobileassetd/softwareupdated (~04:29 PT both nights) plus bird.
- **Discipline on the causal claim.** The consult recorded bird (99%
  CPU uploading the prior window's 10.4 GB backup) as *plausible
  trigger and objective preflight violation* — explicitly NOT confirmed
  root cause. The distinction is what kept the relaunch decision
  honest: launch 2 proceeded under a hardened protocol (bird-SIGSTOP
  with identity custody and a fail-safe CONT trap) plus a predeclared
  budget (frozen chain unchanged, built-in retry pair only, night
  closes if the gate aborts again), rather than on a claimed fix.

**Outcome:** launch 2 passed pre-calibration on the first attempt
(b_fiducial 0.032787 s) and the window collected its core payload
through to a clean salvage close. The consult cost one bounded session
against an 11-hour runway that two more blind aborts would have burned.

**Process note.** Second recorded instance of the escalation trigger
firing inside a measurement window (first: C-039 addendum II (ii)), and
the first where the consult *refuted the lead's mechanism* while
confirming the lead's decision shape. The pattern holding across both:
the consult's unique value is causal discipline under time pressure —
separating "what we can prove" from "what we are tempted to conclude"
before the next launch is committed.

exec
/bin/zsh -lc "sed -n '2599,2868p' docs/council_log.md" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
## C-041: The D100-BII nested-closure arc — two more cold gates, a third-failure STOP, and the CAL-BRACKET consult (2026-08-03, desk session in Ed's absence)

**Shape.** One desk session ran the two open repair branches
(D100-BII-BINDING-01, CAL-BRACKET-D079-01) and the MINT-GENERALIZE
tooling to their conclusions, plus two cold gates on the b-ii
nested-content closure. All delegated; magistrate gates: lead full-suite
+ live bench probes at every disposition. Roles: Fable magistrate;
Sol xhigh execution/audit/consult; cold Fable instances + Opus refuter
at the gates.

**D100-BII arc — three formulations, two gates, STOP (full detail:
`.desk/coldgate_d100_bii/`).** The nested-content closure (D-106 clause
3(c)) failed three structural formulations:
- Formulation 1 (position-enumeration) + formulation 2 (key-denylist):
  cold GATE 2 → **D-107**, adopting the refuter's C-A′ producer-derived
  admission grammar with per-leaf value domains; scope expanded to the
  inventory grammar + the 769/769 false-refusal repairs; row acceptance
  amended with an over-refusal gate (license 3/3 real subjects). The
  refuter's fifth consecutive material amendment: it proved the license
  tool refused all three real subjects at the inventory gate at every
  head, that fix-1 over-refused 769/769, and that four value channels
  stayed open.
- Formulation 3 (open-superset leaves): fix-2 implemented C-A′ but left
  free-text `node_cleanup.error/.path`, the argv superset, and numeric
  leaves open — bench-confirmed workload text licenses. Cold GATE 3 (two
  cold Fable instances converged on L-A surface-refusal; Opus refuter
  DECISIVE): the refuter proved (a) the packet censused the wrong
  population (telemetry.command 0/26 on the license surface, and L-A's
  natural implementation false-refuses 772/772 via a second .command[]
  path), (b) four MORE open carriers, (c) **structurally**, the grammar
  constrains values but not list CARDINALITIES — an unbounded list over
  a closed alphabet is an unbounded workload channel (fires D-107 clause
  7's second return trigger), (d) ~1.2 KB of free numeric-leaf capacity
  remains under any grammar, the same order as the workload output, so
  clause (c) **cannot achieve D-100's "zero output bytes" predicate by
  any bench formulation**, and (e) the substitution attack (c) was
  ordered to close is **already closed by the landed clause (b)**
  hash-sealed manifest pin — so (c)'s real residual is against a careless
  closure author, not substitution.
- **Magistrate disposition: STOP the bench loop, escalate to Ed
  (D-108 pending).** Not a fourth round — three formulations + a
  structural-impossibility finding + a proposal to retire a ratified
  clause is exactly the sunk-cost pattern rule 11 exists to halt.
  Nothing committed; fix-2 diff held untrusted; window B stays blocked.

**Per-layer scorecard (this arc):** the Opus refuter layer amended or
overturned the disposition at BOTH gates (2 and 3) — now the sole
highest-unique-catch layer across SIX consecutive gates. Cold Fable
instances: converged correctly on shape both times, but neither reached
the structural cardinality/capacity finding — the cross-model pairing
earned its keep again (a fresh Fable shares the magistrate's own
dispositions). Packet hygiene: the refuter recorded FOUR findings against
the magistrate's gate-3 packet (selective clause-7 quotation omitting the
half that decided the gate; flags not quoted in full incl. the blocking
anti-round-3 disposition; a laundered "769/769 admit" number; wrong-
population census) — the same classes recorded at D-106/D-107. Standing
correction adopted (recorded in the gate-3 synthesis): quote governing
clauses to the period, quote every source flag in full including the ones
cutting against the proposed disposition, census the license-surface
population.

**CAL-BRACKET arc — consult over blind round three.** Impl + fix-round-1
(first-audit blockers cleanly closed) → delta re-audit FAIL, 3 freshness
blockers, estimator-digest a REPEAT signature. Per the escalation trigger
the next spend was a read-only Sol xhigh DESIGN CONSULT, not a fix round.
It resolved each against D-102: F1 (freshness=6-field epoch) determined;
F2 (4-module estimator digest set) magistrate-ratified from the
b_fiducial_s dependency graph; **F3 (cross-root trigger observability)
escalated to Ed (D-109 pending)** — D-102 mandates the triggers but no
authoritative universe/registry exists; build one vs. narrow D-102 is a
claim-soundness call. Held for a single combined fix round after Ed rules
F3 (it controls the artifact schema). Detail: `.desk/calbracket_d079/`.

**MINT-GENERALIZE-01 — landed.** Full gauntlet (impl → audit → fix →
delta clean → bench fix → lead gates → PR #96 green CI) merged under
D-072; live 7B mint stays lead-reserved. The clean case of the session.

**Process finding for the skills.** Two claim-machinery closures this
session hit genuine DECISION-LEVEL gaps (a clause that cannot meet its
predicate; a mandated trigger with no defined mechanism) that the
adversarial bench correctly SURFACED rather than papered over. The
system worked precisely because the escalation triggers were honored
(consult-not-round-three on CAL-BRACKET; STOP-not-round-four on D100-BII)
— the opposite of the 2026-07-26/27 failures that motivated rule 11.
Recorded as evidence that the topology holds when the loop-immersed agent
actually chooses to stop.

## C-042: Ed-requested pre-ruling debate — 2 Sol xhigh rounds over the D-108/D-109 packets, both packets materially changed (2026-08-03)

Shape: bounded 2-round adversarial consult (MCP discussion lane,
read-only, thread `019fc9bb-73fd-7042-8faf-2a72d74ee5b3`), Sol
instructed to bench-verify packet claims rather than trust them, given
the magistrate's recorded selective-quotation history. Ed then ruled by
explicit deferral to the joint position → D-108 + D-109. Full record:
`docs/process_traces/2026-08-03-d111-backfill/debate-d108-d109/` (tracked).

Unique catches, by layer:
- **Sol round 1 (packet audit):** (1) the D-108 packet's "three
  subjects manually verified" overstated the durable record — full
  b-ii facts exist for the two r08 attempts only; (2) the packet's
  A-min formulation was UNSOUND as stated — writer crash-window
  (capture state created pre-receipt, pre-manifest failure exits)
  defeats publish-on-return receipts, and baseline-prefix ⊆ current is
  not anti-rollback; (3) L-A′ "verified" was a summarized result, not
  a banked executable artifact. All three lead-verified at the bench
  and adopted (reservation-first + independent head pin now R1 law).
- **Sol round 2 (code refutation):** the magistrate's two-subject
  license-surface counter was WRONG — the closure loader requires
  exactly three D-087 occurrences and inspects every one; evidence
  surface ≠ exclusion target. Adopted into D-108 clause 2.
- **Magistrate (context the peer lacked):** schedule pressure LOW
  (recorded), metrology-centric pivot (instrument is the product), and
  shared-R2 marginal-cost analysis — flipped Sol's B recommendation to
  A-min-with-reservation, withdrawn on the record.
- **Convergence quality:** two Sol catches survived verification, one
  magistrate counter died to code, one Sol recommendation flipped on
  supplied context. Both directions of the bridge earned their spend;
  the consult-before-ruling shape (rule 2 amended default) validated
  again on a decision-level packet.

Residual Sol dissents preserved in D-108/D-109 text: three-occurrence
evidence surface; 32/6 dispositions need raw-physics backfill before
issuance; A-min threat-model honesty clause.

## C-046: Retrospective — CAL-REBRACKET-01 max-bracket consumption gauntlet (2026-07-26)

**Retrospective record, authored 2026-08-03 for CRB-6.** This entry
reconstructs the missing council row from the completed `CAL-REBRACKET-01`
table record in `TASK_QUEUE.md` and the durable 2026-07-26 session record at
`docs/process_traces/RESUME-2026-07-26.md`; it does not invent a
contemporaneous transcript.

Shape: two parallel independent design consults rejected persisted derived
summaries and converged on D2+ — authenticated re-derivation at consumption
time under `max(B_pre, B_post)`. Three implementation rounds and three
independent adversarial audits then converged clean. Outcome: PR #86 merged as
`7b12f20`; replayed a9 (7 members) and a10 (37 members) both passed
consumption with every member widened and point estimates unchanged. The lead
gate recorded 2164 passed / 21 skipped at the rebased head, with all five CI
checks green.

## C-047: The 16h runway — two gauntlets, the winB STOP gate, the concurrent-sweep interception (2026-08-03)

Full record: `docs/run_reports/2026-08-03-16h-runway.md` (the ONE
home); decisions D-108..D-112. Shape: Ed-granted autonomous runway with
joint Fable+Sol decision authority; a PARALLEL Fable instance delivered
the two-week soundness sweep mid-runway (Ed-initiated concurrent-audit
pattern — validated, memorized, D080-TRIGGER-01 queued).

Unique catches by layer: Sol audits — D-108 F1 (retirement
over-drop), D-109 B1/B2 + four weak fences; Opus contract refuter —
expired NEG-8 bound, cascade-spelling falsification, F7 barred-cell
scope question, falsify-by-removal sole-cause proof; cold Fable —
stage-1-clean control-flow proof, spelling-collision (two producers),
masking-latency explanation; concurrent sweep — RT-1 (intercepted the
in-flight 7B-mint license neither in-session consultant could see);
lead bench — two fix commits, clause-(d) re-record, byte-identical
pinned replay, exit-status-masking recurrence self-caught. Fix rounds
introduced defects twice more (data #11, #12). Both gauntlets held;
the deviation escape and rule-11 gates fired as designed; the night's
one claim-surface outcome is HONEST SHRINKAGE (CLAIMS_STATUS §1 =
NONE under D-110) plus a proven-honest toolchain (byte-identical
replay).

## C-048: Integration-collision resolution — consult-shaped amendment, delta re-audit catches a live guard bypass (2026-08-04)

Session: successor magistrate, T3-drive era; the first decision handed
off by C-047's close. Full record:
`docs/process_traces/2026-08-04-calbracket-integration-collision/`
(FINDING + RESOLUTION + both Sol reports) and the consult directory
beside it; policy: D-109 addendum II.

Shape: bounded pre-decision Sol HIGH consult (rule 2 amended; Ed's
effort cap held — no xhigh anywhere this arc) → Sol HIGH enforced-scope
implementation → lead bench diff-read + full-suite replay ON THE
INTEGRATION TREE (2487 OK, exit-0 unpiped) → fresh Sol HIGH delta
re-audit → bench hardening from the auditor's specified fix shape →
merge-ref CI green. Merge itself: harness classifier denies agent
`gh pr merge`; Ed names merges (standing pattern, reconfirmed).

Unique catches by layer: PRE-DECISION CONSULT — the byte-identity
oracle correction (historical-digest replay would have CONTRADICTED
D-110; integration-tree core-vs-wrapper parity adopted instead), the
review-pinned rename, the snapshot-identity regression spec. DELTA
RE-AUDIT — the repr-'None' default spoof PROVEN LIVE against the
rendered-signature pin (guard passed while the core's is-None load
path was defeated), plus the remerge-tree fidelity proof and the
loader-mutation kill of the new regression. LEAD BENCH — the piped
exit-status recurrence self-caught AGAIN (third occurrence; the unpiped
re-run is now reflex, the habit clearly is not), stale RUN_STATE
claims (char captures "collected" that never ran; F1's byte-frozen
framing in active restart text). CI — remains the only layer that
structurally sees the merge ref before merge.

Instrumentation note: two HIGH-effort Sol instruments again produced
blocker-grade unique catches (consult F1, audit F2) — Ed's cap shows
no quality decline through this arc. The delta-re-audit rule (every
fix round) paid for itself on a 127-line mostly-test amendment.

## C-049: The 12h autonomous marathon — issuance through the gate, six PRs, and the fork the first consumption exposed (2026-08-05/06)

Session: Fable magistrate, Ed's 12-hour autonomous window (directive
batch 2026-08-05 ~22:00: effort cap lifted, fast tier specified,
D-113 ruled (c), overnight issuance pre-authorized conditional on the
gate). Full records: `docs/process_traces/2026-08-06-d079-issuance-coldgate/`,
`docs/process_traces/2026-08-06-d110-remint-fork/` (DIAGNOSIS, consult
prompt+response, SYNTHESIS), RUN_STATE checkpoint blocks of 2026-08-06
(morning + afternoon + late), plus the per-arc consult traces of
2026-08-05 in `docs/process_traces/`. This entry is the owed council
record assembled by the 2026-08-07 successor from those artifacts.

Shape, in sequence: (i) four checkpoint audits harvested → D-115
adjudicated (Q2 fixed installation capability w/ binding conditions);
(ii) two rule-11 escalation consults after same-signature counters hit
2 — CGV F3 absolute-path-bypass (consult-adopted restructure replacing
the denylist approach) and QG census observation→absence class (Option
C redesign, magistrate stop-condition set); (iii) fix rounds each
followed by xhigh delta re-audits; (iv) the D-079 issuance rule-11 cold
gate — SPLIT verdict, fresh-Fable PROCEED vs Sol-xhigh contract-lens
HOLD — magistrate UPHELD the HOLD; (v) issuance reframed from "an edit"
to a design-bearing consumer implementation, run through the full
gauntlet (PR #108 consumer, PR #109 execution + ledger genesis import +
5-file test reconciliation; two cold gates, adversarial audit + 3 delta
rounds, exact-bytes dual cold review); (vi) D-116 issued, PR #109
merged on green under D-072 at gate-reviewed head `d85b4f9`; (vii) the
FIRST consumption attempt against the issued regime → structural
finding → Sol xhigh pre-decision fork consult (run
`20260806T165843Z-10884`) → magistrate synthesis.

### Unique catches, by layer

- **Rule-11 cold gate (the flagship):** the issuance HOLD caught that
  the packet was underscoped — F1: `calibration_bracketing.py` had NO
  consumer path for an issued acceptance artifact (a JSON flip would
  have made it unloadable in production); F2: `derivation_sha256`
  covers the whole artifact core, so the assumed "n=19 preserved ⇒
  digest preserved" was FALSE (lead-reproduced). An irreversible ledger
  write paired with a production-refused artifact was prevented. The
  split verdict was synthesized by the magistrate (rule 9), not
  majority-voted.
- **xhigh delta re-audits (fix rounds introduce defects — proven
  again, twice):** QG F1 — idempotent init retry reporting success with
  unresolved directory-fsync durability (introduced by fix round 1);
  CGV B1 — malformed digest arg serialized verbatim into REFUSE
  receipts (live-proved) and B2 — a non-CommonMark phantom fence hiding
  real duplicate headings from the pin check.
- **Oversight/prune lens (cgv-audit-B):** PASS receipt did not bind the
  judge to the validated bytes (post-validation exhibit substitution),
  plus the prune recommendation that reframed F3's whole subsystem —
  the finding that triggered the CGV consult.
- **The consumption attempt itself as a layer:** only the live attempt
  exposed that import-marked receipts are excluded from candidate
  discovery BY DESIGN (CAL-BRACKET arc, retained through issuance), so
  no historical window can pass authenticated max-bracket consumption
  at main — every refusal fail-closed; campaign logs sha-verified
  untouched. Desk review had not predicted it.
- **Fork consult (Sol xhigh):** verified all five historical bracket
  pairs physically exist under the drift screen (the objection is
  provenance completeness, not causality); recommended Option 2 (three
  compact prospective windows) over finite-allowlist historical
  candidacy (Option 1, preserved cold-gated); flagged the D-113
  dependency rewire; supplied the unblocked-regardless desk queue.

### Dispositions and open state at close

D-113 transcribed (`8e68cde`); D-115 on main (`0941cf5`); D-116 on PR
#109; PR #109 merged (`c537386`). Magistrate + consult CONCUR on
Option 2; **Ed had NOT ruled at the machine-move stop** — his ruling,
the prefill-contrast shape ack, and three-nights scheduling were the
owed items handed to the successor (RUN_STATE checkpoint block).

exec
/bin/zsh -lc 'for id in 029 030 031 032 033 034 035 036 037 038 039; do rg -n "C-$id" docs/council_log.md || true; done' in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
1517:| C-029 | 2026-07-11/12 | Agent-lane triple (SITE-01 / P2-049 / P2-028): three standard-tier Sol pipelines, per-stream lenses, lead bench adjudication of 5 blocker claims (2 confirmed, 1 partially refuted, 1 design ruling, 1 reproduce-first — refuters replaced by lead code-reading where cheaper); trace + calibration table in `docs/run_reports/2026-07-12-agent-lane-triple.md` §Process Trace Appendix (the ONE home; no full entry here) | PRs #61/#62/#63 opened at lead-gated heads; lead-gate unique catch: fix round's `succeeded`-only rule would refuse legitimate `capped` cells (FIX-14; third "fix rounds introduce defects" datum); implementer caught a stale kernel authority pointer (half-right — lead archaeology completed it, `507f600`); process defects logged: WRITE_SCOPE in-prompt requirement (3 rc=64), unintended ULTRA effort on all 13 invocations (config passthrough; TOOL-01), upstream outage killed 3 delta-audit attempts (re-audits owed pre-merge on #62/#63) |
1518:| C-030 | 2026-07-13 | Restart close (continuation of C-029; Ed-authorized merges): delta re-audits on #62/#63 finals + post-merge integration review, all explicit xhigh (effort fix held: 3 sessions ≈ 7.0M tokens vs the prior 13 ≈ 118M); two lead bench fixes with defect regressions; trace in `docs/run_reports/2026-07-13-restart-merge-deploy.md` (the ONE home; no full entry) | #61-#63 MERGED; delta-audit unique catch DRA-001 (equal-but-malformed identity hashes counted as identity evidence — fourth "fix rounds introduce defects" datum, this one surviving TWO earlier review layers); integration-review unique catch XSI-1 (installed-wheel CI ran only --help; now smokes both new fail-closed surfaces); lead-live layer: deploy ACCEPTED 854,349 B / routes 5/5 / freshness clear + cross-thread breakage fix (P2-028 kernel retirement vs gen_state fidelity tests, caught by the concurrent bridge thread's suite run); concurrent Claude↔Sol bridge landed same tree, lead-verified 8/8 protocol + 4/4 tests before commit; PAUSE: comprehensive whole-project audit declared next gate (Ed) |
1518:| C-030 | 2026-07-13 | Restart close (continuation of C-029; Ed-authorized merges): delta re-audits on #62/#63 finals + post-merge integration review, all explicit xhigh (effort fix held: 3 sessions ≈ 7.0M tokens vs the prior 13 ≈ 118M); two lead bench fixes with defect regressions; trace in `docs/run_reports/2026-07-13-restart-merge-deploy.md` (the ONE home; no full entry) | #61-#63 MERGED; delta-audit unique catch DRA-001 (equal-but-malformed identity hashes counted as identity evidence — fourth "fix rounds introduce defects" datum, this one surviving TWO earlier review layers); integration-review unique catch XSI-1 (installed-wheel CI ran only --help; now smokes both new fail-closed surfaces); lead-live layer: deploy ACCEPTED 854,349 B / routes 5/5 / freshness clear + cross-thread breakage fix (P2-028 kernel retirement vs gen_state fidelity tests, caught by the concurrent bridge thread's suite run); concurrent Claude↔Sol bridge landed same tree, lead-verified 8/8 protocol + 4/4 tests before commit; PAUSE: comprehensive whole-project audit declared next gate (Ed) |
1519:| C-031 | 2026-07-13 | Bridge v1 (Ed-directed): 3-round Fable<->Sol design discussion held OVER the MCP bridge itself (thread 019f5a67-00f5); Sol out-designed the lead 3x (hard-block leases vs warn-only, path-level baseline manifests vs status digest, split event logs) — all accepted; 5 draft-choices lead-adjudicated; impl + 2 fix rounds + fresh lens + delta re-audit; full record `docs/run_reports/2026-07-13-bridge-v1.md` (the ONE home) | PR #64 MERGED: bridge-protocol/v1 contract + scripts/bridge (atomic hard-block leases — direct fix for the 2026-07-12 cross-thread collision — baselines, 4-verdict scope-check, thread registry) + adapter FAILED-synthesis; lens caught 4 blockers, delta re-audit caught 1 NEW blocker (malformed-override fail-open; FIFTH fix-rounds-inject-defects datum); audit-loop termination ruling: post-fix2 residue lead-verified directly; suite 1358 OK |
1520:| C-032 | 2026-07-13 | Bridge v1.1 (Ed-directed: "fix up the bridge for maximum co-work"): Sol xhigh design consult over the bridge (thread 019f5d1d-b681-7db1-8714-812fdd2f198b; 5 amendments accepted + v1 duplicate-sentinel adapter bug confirmed); ratified spec Sol-implemented; 3 lenses → 3 fix rounds → 3 delta re-audits, finding convergence 13→6→2→1; full record `docs/run_reports/2026-07-13-bridge-v11.md` (the ONE home; no full entry) | PR #65 MERGED `d285989` (Ed named the merge same session after the harness declined agent self-merge): discussion lane, receipt-anchored session-open/close wrappers (session.lock-serialized, write-only in v1.1), tolerant envelope, per-call reverse effort + echo, peer channels + bounded proposal diffs, one-home effort dedup; delta re-audits caught 6+2+1 fix-round findings (sixth/seventh "fix rounds introduce defects" data) incl. two corrections of the lead; suite 1387 OK; CI green on final head 8b96bd4 |
1522:| C-034 | 2026-07-14/15 | Audit fix-wave resume + close-out (Ed's AXI handoff §0.2 sequencing; full record `docs/run_reports/2026-07-14-audit-resume-axi.md`, the ONE home): per-order cadence Sol high/xhigh implement → fresh checker → fix rounds → lead gate; 28 Sol sessions ≈ 251M tokens (ARC HARD crossing recorded in the refreshed WO-022 receipt — gate-closing work, policy landed mid-arc); ULTRA comparison audit (intended, pre-declared) + xhigh integration review + Fable completeness critic + C-033 coherence council | S1 closed (WO-010 NEEDS_SCOPE grant, WO-011 checker-FAIL→fix→delta-PASS), S4 closed (WO-019 PASS-0-findings; WO-031 3-major fix round), WO-027 fix round, WO-021 xhigh 3-phase w/ 8a receipt + 4-record-loss BLOCKER migration, WO-022 verbatim landing; integration tree `impl/audit-integration`: 2 unique integration catches (capsule budget union breach; D-068 vacuous-green surfaces) + ULTRA's 2 blockers/20 findings triaged per Ed's substance-over-ceremony ruling (7 fixed `913a2a6`, 4 bench, 5 queued, rest dispositioned §8.5); D-043 closure (17 lines + 6 lead decision-log amendments); critic's 3 gaps closed same session; suite 1532 OK at `f8f0f92`; PR to main awaits Ed's adoption merge; 3 lease adjudications Ed-approved after classifier refused lead self-approval (correctly, all three times) |
1523:| C-033 | 2026-07-14 | AXI intake council (Ed-directed via `docs/axi-handoff.md` + Ed's batched §5 answers this session): short recorded Sol high read-only coherence review of drafted D-066..D-070 (outcomes Ed-directed, not re-decided; consult ran over the audited CLI path because the MCP server is unavailable in this headless session; prompt/response tracked at `docs/process_traces/2026-07-14-c033-axi-consult/`) | Sol verdict DISCUSSION: outcomes authorized, Ed's four D-067 amendments honored; 6 coherence corrections identified and ALL lead-accepted before commit: explicit supersession of the D-058 token-normalization Primary Metric clause (contract text assigned to S-A, keeping S-0 docs-only), dual-basis-capture bundle-state definition (successful idle-eligible request-level; nullable semantics preserved), D-032 gross-only phase semantics named, deploy convention re-attributed C-012→C-013, registry source homes corrected (C5-* bank vs C-023-*/RQ-* registry per D-055), `request_id` pinned to `events.jsonl` `metadata.request_id` with new-version-only reducer dispatch, D-064 duplicate/mismatched index rows cleaned; remaining deploy-instruction surfaces routed to WO-031 + S-0 |
1522:| C-034 | 2026-07-14/15 | Audit fix-wave resume + close-out (Ed's AXI handoff §0.2 sequencing; full record `docs/run_reports/2026-07-14-audit-resume-axi.md`, the ONE home): per-order cadence Sol high/xhigh implement → fresh checker → fix rounds → lead gate; 28 Sol sessions ≈ 251M tokens (ARC HARD crossing recorded in the refreshed WO-022 receipt — gate-closing work, policy landed mid-arc); ULTRA comparison audit (intended, pre-declared) + xhigh integration review + Fable completeness critic + C-033 coherence council | S1 closed (WO-010 NEEDS_SCOPE grant, WO-011 checker-FAIL→fix→delta-PASS), S4 closed (WO-019 PASS-0-findings; WO-031 3-major fix round), WO-027 fix round, WO-021 xhigh 3-phase w/ 8a receipt + 4-record-loss BLOCKER migration, WO-022 verbatim landing; integration tree `impl/audit-integration`: 2 unique integration catches (capsule budget union breach; D-068 vacuous-green surfaces) + ULTRA's 2 blockers/20 findings triaged per Ed's substance-over-ceremony ruling (7 fixed `913a2a6`, 4 bench, 5 queued, rest dispositioned §8.5); D-043 closure (17 lines + 6 lead decision-log amendments); critic's 3 gaps closed same session; suite 1532 OK at `f8f0f92`; PR to main awaits Ed's adoption merge; 3 lease adjudications Ed-approved after classifier refused lead self-approval (correctly, all three times) |
1521:| C-035 | 2026-07-15 | AXI spec-design phase (Ed: "design as many specs as you can with help from sol"; arc opened post-clearance with predeclared deliverable per WO-022 §5a): three parallel Sol spec pipelines (SA xhigh / SD high / SE xhigh), each author -> fresh counterreview -> fix round(s) -> delta -> lead termination; ~14 Sol sessions ≈ 71.2M tokens (est.); full trace in the 2026-07-14 run report §AXI spec-design phase | Specs landed `1464c93`/`d2bd5ee`/`3b5c4bf`: SA burst-decode contract (implementation-ready; honest frozen-arm goldens after the counterreview refuted byte-identical vs actual code; deterministic anti-top-up ledger), SD pair scorecard (four-option D-016 decision box for Ed; forced-continuation memory probe), SE six AP drafts (estimand demotion on AP-REASON-VARIANCE; union-bound + Markov-quantile floor guards; 21 PROVISIONAL cells with named triggers); 30+ counterreview findings fixed pre-landing; 3 benign lease-close artifacts pending Ed batch adjudication |
1525:| C-036 | 2026-07-16 | Resumption + no-hardware batch (Ed: audits in a workflow + "handle the merge yourself if all is well... get the project ready for my quiet mac"; full record `docs/run_reports/2026-07-16-resumption-nohw-batch.md`, the ONE home): ultracode readiness workflow (4 Sol-high audits + severity-tiered refuters) BEFORE work selection; then 4 streams (SPLIT-AP xhigh contract tier, SITE-02 high standard, AXI-SB xhigh spike, AXI-SD Fable web-verification); every fix round delta-re-audited; three self-merges under Ed's in-session delegation, each with the full D-031-amended gate | PRs #67 (`7593259`, AXI-SA + CI portability fix after the audit caught red CI), #68 (`2778ed2`, SITE-02 — D2 step verified EXECUTED in the CI log), #69 (`9db4546`, SPLIT-AP freeze) merged; integration review 0 cross-stream defects, merged main 1630 OK; kernel closures 51→48 IDs; AXI-SB live probes (lead-run, B∈{2,4}) → verdict `supported`, Mac C5-2.2 leg mint staged on `impl/axi-sb` (effective on its merge); delta re-audit caught a LEAD-pinned predictor defect (8th fix-rounds-inject-defects datum, first lead-authored); AXI-SD memo: OLMo pair d_active 0.0016 + 8GB-fit may moot Option A's premise, Qwen3 pair confirmed-fails G10 (17.17 GB) |
1524:| C-037 | 2026-07-17 | Window-A execution + wrap arc (Ed: floors-first overnight -> advisor deadline -> site rebuild -> exploratory breadth; full records: the two 2026-07-16/17 run reports, the ONE homes): four-failure shakedown story (stale-bundle reuse, wallpaper idle contamination caught by sentinel, 34.6ms trace-boundary bracket via two live-bundle triages, stale-lock exit-0 wart) -> canonical PASS; 248-line/222-bundle floor campaign verified by 8-agent ultracode extraction; advisor brief + README-first site + Learn guide (Ed deployed); exploratory 9-bundle block; DSpark/DFlash feasibility confirmed; D-071..D-075 recorded | PRs #72-#75 merged under D-072 standing authority; delta re-audits caught blockers twice more (10th datum incl. lead-pinned formula defect); fold-in round's refusal caught a forced-report placeholder trace; scope enforcement caught the lead's own stray file (adjudicated benign); floors: request 0.527/0.052 J, phase 1.477/0.786 J, ABBA comparative w/ flagged tail drift; exploratory gross suite: OLMoE ~229 J vs Qwen3-4B ~362.8 J vs 122B ~1072 J (exploratory-labeled) |
72:| C-038 | 2026-07-25/26 | FLOOR-LABEL-01 gauntlet close (D-078 cl.11 labelled attribution-limited floors) + quiet-window collection; Ed re-proportioned the instrument mix mid-session (Opus 5 subagents = primary delegated lieutenant, Fable on genuine need, Sol = execution workhorse, lead adjudicates); full entry below | Opus-contract lens verdict COMPARATIVE COVERAGE: COMPLETE with 4 should-fix / 4 nits, incl. the `_combined_floor` key-sniffing misattribution mirrored bug-for-bug into `artifact.py` (so validation recomputes the same wrong answer and ships) and the ratio-unit floor/diagnostic inversion; Sol xhigh audit's 1 blocker (runnable V3 probe: comparative blocks minted WITHOUT admissible half-widths validate clean, floor_gate 5e-324 J vs 2.6484 J) ADJUDICATED DOWN to registered limitation L1 — first concrete demonstration of L1, and FLOOR-LABEL-01 recorded as modestly WIDENING its blast radius; Sol xhigh clock diagnosis root-caused window C to transient wall-vs-monotonic slew over the 5 ms ceiling (7.769 ms verified) and corrected the lead's duration hypothesis; Fable adjudication (zero tool uses, 108 s) OVERTURNED the lead's own self-diagnosis and named the disposition (rigorous on work products, exempts its own premises about the environment) → rules R1/R2/R3, no demotion; window B 59/59 clean (whole-window verdict PENDING), window C failed twice on clock slew, window D not started; FIVE lead errors recorded, incl. the ~10-hour lost quiet window (untracked `nohup` + turn ended with no wake source) and TWO exit-status masking incidents → generalization: EXIT STATUS IS NOT EVIDENCE OF WORK DONE |
1891:## C-038: FLOOR-LABEL-01 gauntlet close + quiet-window collection — an instrument-mix re-proportioning, a lost quiet window, and two exit codes that lied (2026-07-25/26)
1526:| C-039 | 2026-07-28 | Mint-implementation session (Ed: resume per RUN_STATE, then "merge on green + start the mint consult"; magistrate topology; full record `docs/run_reports/2026-07-28-floor-mint-implementation.md`, the ONE home): PR #87 gauntlet (2 Sol xhigh lenses + 5 Sol high refuters + 1 Opus contract refuter, lieutenant-directed), E4 fix + CLEAN delta re-audit, D-081 parser ruling (Ed, async question), Sol xhigh mint design consult (3 DISAGREEs sustained -> D-082), 7-stage xhigh implementation, suite-pruning consult (0 removals clear D-061) | PR #87 MERGED `058c918`; `impl/mint-tool` pushed unmerged (review owed); C1 SPLIT (Sol nit vs Opus should-fix) magistrate-synthesized to should-fix, closed via ratified Q4; 5 broken-wake incidents -> tracked-poll pattern folded to codex-delegation; lieutenant self-flagged 2 retracted fabricated verdict narrations (mechanism removed); concurrent-session force-push anomaly flagged to Ed; **ADDENDUM at the end of this file** records the 2026-07-29/30 continuation (FIX-6..9 gauntlet, three cold gates with paired Opus contract-lens refuters, mint #1, the 7B floor window; rulings D-083..D-088; D-088 recorded in the same-day close-out); **ADDENDUM II** records the 2026-07-30/31 escalation consults (cooldown-join design consult → D5-J/D-089; contrast-window recovery consult, the first trigger firing inside a measurement window) |
2118:## C-039 addendum: the FIX-6..9 gauntlet, three cold gates, and the 7B floor window (2026-07-29/30)
2120:Continuation of the C-039 index row above, covering the arc that carried
2260:## C-039 addendum II: two escalation consults — the cooldown-join design consult and the contrast-window recovery (2026-07-30/31)
2262:Second continuation of the C-039 index row. Both entries here are **consults
2361:## C-039 addendum III: the clock-anchor knife-edge consult (2026-08-01, in-window)
2410:firing inside a measurement window (first: C-039 addendum II (ii)), and

codex
A key governance correction emerged: the log’s old “two zero sessions → drop” rule was superseded by D-061. The current rule is three mechanically applicable exposures triggering an expected-loss review, with safety/final-head/integration layers protected from automatic deletion. I’ll report both the observed zero streaks and whether they are actually eligible, rather than calling a protected layer disposable.
exec
/bin/zsh -lc "rg -n -i -C 2 'lead["'^'"\\n]*(error|defect|miss|wrong|stale|over|guessed|fabricat|piped|exit|index|bookkeep)|prompt-defect|piped|exit-status|index row|index-row|RUN_STATE stalen|stale RUN_STATE|stale gate|selective quot|packet hygiene|two-writers|whole-file "'`--theirs`|scope.*lead|lead.*scope|wrong-population|wrong population|dictat|bookkeeping'"' docs/council_log.md" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
17-Standing council roles (adopted C-001; process decision D-031):
18-
19:- **Claude (lead/orchestrator)** — scopes work, diagnoses live/hardware
20:  failures, runs adversarial review workflows, owns bookkeeping and the
21-  final merge decision, and is the only member that touches real
22-  hardware.
--
52-| C-008 | 2026-07-07 | Multi-stream hardware-prep session (4 streams, Opus directors + Codex volume), user-checkpointed mid-flight | 3.0.1 verdict replay_supported; P2-013 groups 1-4 (19/31 pins); 2K protocol v1 provisional; DOC-007 done; Slice 2O landed; ledgers v2 + calibration + wake-gap lessons folded into skills same-session |
53-| C-009 | 2026-07-07 | META-REVIEW of the orchestration system itself (user-directed): 2 blind Codex analyses vs Fable's blind positions → conferral → SIGNED consensus | Hybrid topology + lead stream-state table; foreground-wait orchestrators + STALLED-handback; heartbeat demoted to backstop; Codex up-stack (design freedom, schema drafts, lead-decision packets); docs single-writer end-state (run report = session record; council log = deliberation only; RUN_STATE = pointer; ledgers retire at integration WITH branch/hash pointer); retired-artifact pointer rule; codex-run patch queued; preflight gates (device inventory, quiet lock, provisional labels) |
54:| C-010 | 2026-07-08 | Resume+merge session — first full run under the C-009 topology (pointer entry; full record in the resume-merge run report) | Lead-driven pipelines validated (zero stalls, no subagent directors); B-14/B-15 wire pins overturned by lens review pre-hardware; fabricated-evidence defect caught at lead diff gate (B-44); Ed grants standing self-merge-with-review authority; final-head review rule adopted; PRs #8/#9/#10/#11 merged |
55-| C-011 | 2026-07-08 | Counter-review of the independent project critique (4 verification lenses + 5.5-high adjudication; full entry below) | Critique findings adjudicated into mechanics: fail-closed campaign runner, counterbalanced order manifest, reducer honesty flags, claims ladder (D-037), P2-015 ranked before 2M; merged as PR #12 |
56-| C-012 | 2026-07-08 | Site observatory stream (pointer entry; full record in run report `2026-07-08-site-observatory.md`) — dual-prior design round, 2 image-critique rounds, visual sign-off, counterreview, final-head gate | Data-driven status frontend merged as PR #13; fail-closed parser honesty enforced (2 counterreview blockers fixed); P2-017 per-source stamps closed; image-heavy analysis routed to Codex as standing doctrine (Ed) |
57-| C-013 | 2026-07-08 | Lakebed deployment stream (pointer entry; full record in run report `2026-07-08-lakebed-deploy.md`) — 5.5 impl + 6 platform-constraint fix rounds + fresh counterreview | Site live as a shareable capsule with a live GitHub freshness layer (fails soft); lead owns deploy/claim (no sandbox network); site regen+redeploy folded into the RUN_STATE end-of-work loop |
58:| C-014 | 2026-07-08 | Workload-suite science hardening (full entry below) — lead audit + scout + 3 design lenses + invited peer counterreview | Q4-at-L3 gap closed via `q4_l3_shape_grid_v1` (4x3 + holdouts); P2-015 expanded to comparative MDE floors; jw_mixed common-shape stratum (C-W.1 was unfalsifiable); P2-010 split substrate/smoke, scored ladder deferred; two-quiet-window plan; analysis-plans contract (D-038); program restructure (D-039); two lead designs overturned by invited peer |
59-| C-015 | 2026-07-08 | Benchmark expansion council (full entry below) — reach lenses R1/R2 + design lenses E1/E2 + peer counterreview | Suite architecture v2 (D-040: B×k bundles, one generic mechanism, per-item status model); interop direction (D-041: HumanEval-first imports, marker-shim energy layer, kill list); capability map landed in bank; R2 collect-now set spawned the window-a-capture stream; capstone stop-line + D-034 gate restated |
60-| C-016 | 2026-07-08 | Post-large-workload meta-reassessment (pointer entry; records: D-043, `~/.claude/skills/skill-usage-log.md`, run report addendum) — 4 analysts (council/decision/skill mining + cold-start derivability) + completeness critic, Workflow-orchestrated | Supersession drift named as THE recurring unfolded failure mode (~70% of doc defects) → D-043 write-time + sweep-time discipline; operative merge-authority contradiction fixed; 5 skill divergences fixed; codex-delegation rewritten procedure-first; clean-machine derivability closed (scripts/codex-run committed + orchestration.md pointer map); §10 post-large-workload trigger now standing |
61-| C-020 | 2026-07-08 | STOP-AND-ANALYZE WHOLE PROJECT: technical + research merit debate (full entry below) — 69-agent Codex assessment workflow + 2 independent Fable position papers + recorded Fable-vs-Codex debate; owner-directed | Merit verdict recorded (docs/reviews/2026-07-08-technical-merit-review.md); D-048 model-first split program + D-049 transfer-boundary accounting promoted; question ranking adjudicated (Q4→Q1 coupled #1, Token-Shape Null sustained #2, Q6 elevated #3, affine ladder = validity instrument); crossover prior corrected by arithmetic; cheap-validity priority set (bundle publication + external re-reduction first); repo-verified gaps: bundles unpublished, no LICENSE, D-033 strict-validation legacy bypass |
62-| C-019 | 2026-07-08 | Post-suite-build meta-reassessment (full entry below) — 4 analyst lanes (5.5-direction study over 43 invocations; calibration longitudinal; project status/value ranking; closure) + completeness critic | Direction doctrine folded into codex-delegation skill (precedence/autonomy/FIX-N/production-gate clauses; model-version scoping rule pre-upgrade); D-013 prose back-annotated marker-bounded; shakedown gate added to P2-015; P2-025 adjacency + P1-008 elevation (incl. examiner acceptance-bar ask); pre-#21 corpus validity noted (dict-read-scale overhead, no re-reduction); watch items: integration-after-oversight, Opus A/B |
63:| C-018 | 2026-07-08 | D-013 alignment-capture window fix (parallel session; full entry below) | sampling_stopped stamped before alignment capture (PR #21: `255a7e6`, bookkeeping `c2e51b2`, merge `49c5b66`); suite 734; D-013 prose back-annotated to marker-bounded wording in the reassessment batch |
64:| C-017 | 2026-07-08 | Suite-build adjudication + implementation gates (full entry below) — Codex disposition draft + fresh adversarial round + lead calls; 11 unit lenses + 1 Opus outage substitute + 7-reviewer oversight + 3 final-head + integration | 37 amendments dispositioned → D-044..D-047; substrate/ladder/generators BUILT and merged (PRs #17/#18/#20/#19, suite 732); 3 lead live-only catches (refs, strict rollup, sampler namespace); oversight caught 2 validation holes pre-merge; PR #18 base-retarget slip recovered via #20 |
65-| C-021 | 2026-07-09 | Advisor status-site live-depth refresh (pointer entry; D-051; run report `2026-07-09-advisor-status-site.md`) | Static generated pages remain the audit fallback; Lakebed gets fail-soft live overlays from current GitHub markdown; Story page volatile counts removed; advisor cockpit expanded with attention, readiness, evidence, and claim-ceiling panels; gpt-5.5-high counterreview used before deploy |
66:| C-022 | 2026-07-09 | CP-5 resume session (pointer entry; run report `2026-07-09-cp5-resume.md` owns the full trace) — lead-driven, ~35 codex sessions: implementation, fix rounds, 12+ lenses/final-head passes, 2 integration reviews | PRs #22..#28 merged (merge-gate shape held: lens→fix→lead live gate→fresh final-head→CI→merge); final-head layer caught 3 blockers + 7 should-fixes post-lens; CI merge-ref caught the one cross-branch interaction (#23 fixtures × #27 strict rules) no other layer could see; 1 lead prompt-defect (inferred-sidecar pin) caught and refixed; methodology synthesis + suite_next packet adjudicated (CP-6); D-047 sampler clause amended (fail-closed); stop card CLEARED; Window-A GO |
67:| C-023 | 2026-07-09 | Scientific-rigor review of the measurement suite, benchmark, and full question bank (user-directed; full record `docs/reviews/2026-07-09-scientific-rigor-review.md`) — 4 fresh 5.5 lenses (metrology, benchmark/stats, per-question bank audit, advisor simulation) + independent lead read + 1 bidirectional discussion round | Verdict: strong provisional, advisor sign-off after a named all-software artifact list (error budget/P2-015 combined spec, analysis registry + multiplicity policy, canonical RQ registry + linter, frozen headline, contrast-level stats amendment, ordering executability, token-normalization contract); every blocker no-hardware-fixable; C5-1.1 blocker OVERTURNED in discussion (already contract-capped by C-014/D-037); ordering gap (C-015 promise vs manifest_order execution) elevated to pre-campaign; queue impact deferred to the step-2 planning session |
68-| C-024 | 2026-07-09 | Spec-fleshing wave 1 (pointer entry; run report `2026-07-09-spec-fleshing-wave1.md`) — 4 worktree streams (5.5 implement), 4 counterreview lenses, 3 fix rounds, 4 final-head + 1 tail-verification pass, integration review | PRs #29..#32 merged (D-052..D-055 ratified: scope contract, contrast-level stats + registry, false-effect guard floor, RQ registry); R2's estimator kill (percentile-UCB unidentifiable at n=10) was the session's decisive catch; integration review caught 5 cross-stream seam drifts (S1/S2 written against pre-S3 contract text); P2-015-PREP (queue rank 0) closed; checkpoint-push cadence adopted mid-session (Ed) |
69:| C-025 | 2026-07-09 | Wave 2 — ultracode workflow build (pointer entry; run report `2026-07-09-spec-fleshing-wave2.md`) — 46-agent workflow (4 impl streams, 8 lenses, severity-tiered refuters) + 2 lead-driven reinforcement streams + 6 final-heads + tail verification + combined-ref check + integration review | PRs #33..#38 merged (D-056..D-059 ratified: order policies + order_row, drift-is-a-bound + stable reason codes, token-normalization contract, claims-lint CI enforcement); refuter layer killed 10 findings pre-triage; final-heads caught 2 live-path defects (MLX position under rotation; linter false-negative regression); mutation testing debuted in the test-audit lens; combined-ref suite check validated the p2029 x p2030 strict-surface interaction pre-merge; suite 877 |
70-| C-026 | 2026-07-09 | P2-034 broad campaign packs (pointer entry; run report `2026-07-09-p2034-broad-packs.md`) — design-round-first (memo ratified w/ 3 pins), single worktree stream, dual lenses, final-head CLEAN | PR #39 merged; six packs, pack lint errors=0; compliance lens caught a char-level registry drift the linter cannot see (code-span nesting) + a scorer-leak + P2-022 structure flattening; executability lens caught the external-lab cold-start gap; pre-hardware campaign surface COMPLETE (every pre_hardware_preparable=fully row packed) |
71-| C-027 | 2026-07-09 | Whole-project council review with gpt-5.6-sol xhigh (first production session; 7 lenses: topdocs/rigor/stats/meta/reverse/arch/negspace + counterreview + independent Fable-tier final examiner; full record `docs/reviews/2026-07-09-c027-whole-project-review.md`) | 8 blocker clusters confirmed (token-denominator mislabel, superseded D-053 prose, RUN_STATE dual next-action, claim machinery unimplemented+unowned, empty D-050 manifest, four D-031 direct-to-main commits, evidence-integrity trio, protocol blockers); claim surfaces corrected same session; 14 follow-up queue rows + NV-GATE-2 additions to P2-005; D-060 proposed + D-061..D-063 accepted; counterreview reversed the lead twice (legacy-gate framing, restructure staging) |
72:| C-038 | 2026-07-25/26 | FLOOR-LABEL-01 gauntlet close (D-078 cl.11 labelled attribution-limited floors) + quiet-window collection; Ed re-proportioned the instrument mix mid-session (Opus 5 subagents = primary delegated lieutenant, Fable on genuine need, Sol = execution workhorse, lead adjudicates); full entry below | Opus-contract lens verdict COMPARATIVE COVERAGE: COMPLETE with 4 should-fix / 4 nits, incl. the `_combined_floor` key-sniffing misattribution mirrored bug-for-bug into `artifact.py` (so validation recomputes the same wrong answer and ships) and the ratio-unit floor/diagnostic inversion; Sol xhigh audit's 1 blocker (runnable V3 probe: comparative blocks minted WITHOUT admissible half-widths validate clean, floor_gate 5e-324 J vs 2.6484 J) ADJUDICATED DOWN to registered limitation L1 — first concrete demonstration of L1, and FLOOR-LABEL-01 recorded as modestly WIDENING its blast radius; Sol xhigh clock diagnosis root-caused window C to transient wall-vs-monotonic slew over the 5 ms ceiling (7.769 ms verified) and corrected the lead's duration hypothesis; Fable adjudication (zero tool uses, 108 s) OVERTURNED the lead's own self-diagnosis and named the disposition (rigorous on work products, exempts its own premises about the environment) → rules R1/R2/R3, no demotion; window B 59/59 clean (whole-window verdict PENDING), window C failed twice on clock slew, window D not started; FIVE lead errors recorded, incl. the ~10-hour lost quiet window (untracked `nohup` + turn ended with no wake source) and TWO exit-status masking incidents → generalization: EXIT STATUS IS NOT EVIDENCE OF WORK DONE |
73-| C-040 | 2026-08-01/02 | Commit-3 cooldown-join gauntlet: five fix rounds and three cold-gate dispositions | PR #93 merged after the custody micro-commit and exact-set pin; D-105 recorded the residual recognizer boundary; every review layer produced unique catches |
74-| C-041 | 2026-08-03 | D100-BII nested-closure arc and CAL-BRACKET design consult | Three closure formulations failed and the bench loop stopped for decision-level rulings; CAL-BRACKET F3 escalated; MINT-GENERALIZE tooling merged |
75-| C-042 | 2026-08-03 | Ed-requested pre-ruling debate: 2-round adversarial Sol xhigh consult over the D-108/D-109 decision packets (MCP discussion lane, read-only; Sol instructed to bench-verify packet claims; record .desk/2026-08-03-sol-debate-d108-d109.md); Ed then ruled by explicit deferral to the joint position | Both packets materially changed before ruling: Sol caught the overstated three-subject manual-verification claim and broke the original A-min formulation (writer crash-window; prefix-subset is not anti-rollback) — both lead-verified and adopted (reservation-first + repo-committed head pin now D-109 law); Sol's code refutation of the magistrate's two-subject license-surface counter adopted into D-108 clause 2; magistrate context (schedule slack, metrology pivot, shared-R2 marginal cost) flipped Sol's B recommendation to A-min-with-reservation, withdrawn on the record; residual dissents preserved in both decision texts |
76:| C-043 | 2026-07-22 | D-078 P0 instrument-repair close-out (round-8/8b landing + §C-028 delta re-audit with 3 lenses / 11 refuter runs, round-9 FINAL confirmation, L1 adjudication, PR #79) | Round-8b delta re-audit caught the understated-B_fiducial ClockStamp blocker two audited rounds missed; refuters killed 2 findings, narrowed 1, split 1 (lead-synthesized); CR9-1 adjudicated as registered limitation L1 + FLOOR-BIND-01; failure modes recorded (content-filter refuter kills -> data-quality rephrase; bench-edit-during-enforced-scope false attribution; review-genre null-final recovery) |
77:| C-044 | 2026-07-24 | NEG-8 drift-gate estimand debate (Ed-directed pre-ratification cross-model debate; Sol xhigh peer vs lead ruling) | Peer disagreed on inferential role (screen != stability proof) and was adjudicated CORRECT; Ed ratified the amended screen+budget design (option F full) with rigor-spiral + no-invented-physics guardrails; second recorded case of peer design judgment overturning a lead ruling pre-implementation |
78-| C-045 | 2026-07-24/25 | NEG-8 SCREEN+BUDGET audit gauntlet: four audit rounds and paired contract/execution refuters | PR #85 merged after three fix rounds; the paired lenses materially changed triage, and the residual custody-hardening work was queued |
79-| C-046 | 2026-07-26 | Retrospective: CAL-REBRACKET-01 max-bracket consumption gauntlet (PR #86) | Governed consumption-time authenticated re-derivation landed after three implementation rounds and three independent audits; a9/a10 replays passed with widened members and unchanged point estimates |
80-| C-047 | 2026-08-03 | The 16h runway (Ed-granted; joint Fable+Sol decision authority; concurrent sweep instance mid-flight): D-108/D-109 debate+rulings executed, D-110/D-111 sweep-triggered rulings, winB STOP cold gate -> D-112, two Sol gauntlets, pinned byte-identical mint replay, checkpoint for harness switch | D-108 closed via PR #99 + re-record; CAL-BRACKET held at 2e61ff9 (B1 residual, rule-11 gate owed); winB license exhausted as drawn (r06 disposition parked for Ed); mint chain D-110-blocked; CLAIMS_STATUS section 1 honestly NONE; sweep propagation fixes landed; layer yield in the run report |
81:| C-048 | 2026-08-04 | Integration-collision resolution on the CAL-BRACKET-D079-01 lead gate: bounded pre-decision Sol HIGH consult -> consult-shaped signature amendment -> fresh delta re-audit -> bench guard hardening -> merge-ref CI | The delta re-audit PROVED a live repr-'None' default spoof against the rendered-signature guard (hardened with a regression); the consult corrected the byte-identity oracle to integration-tree core-vs-wrapper parity (a historical-digest replay would have contradicted D-110); lead integration-tree replay 2487 OK exit-0 unpiped; PR #100 gate-complete, merged 2026-08-05 (`f75d12b`) |
82-| C-049 | 2026-08-05/06 | The 12h autonomous marathon: six PRs (#102-#104, #106-#108) + PR #109 issuance gauntlet; two rule-11 escalation consults (CGV F3 closure, QG census Option C); the D-079 issuance cold gate (split verdict, HOLD upheld); D-113/D-115/D-116; then the first re-mint consumption attempt exposed a structural closure -> Sol xhigh fork consult | The cold gate's HOLD prevented an irreversible ledger write paired with a production-refused artifact (F1 no-consumer-path, F2 digest-role coupling — issuance reframed as implementation and re-gauntleted as PRs #108/#109); xhigh delta re-audits again caught introduced defects (QG init-durability F1; CGV live-proved receipt-serialization B1 + phantom-fence B2); historical max-bracket consumption proved structurally closed at main — Option 2 (three fresh prospective windows) recommended by consult + magistrate; Ed's ruling OWED at close |
83-
--
113-  Claude's orchestration decisions (flagship config mutation, 20 Hz mock
114-  workaround, provisional D-016 wording, main-branch convention,
115:  bookkeeping fidelity).
116:- Findings that survived: (1) stale gate-state prose in 6 files
117-  (Opus sweep + Codex independently convergent) — README/playbook test
118-  counts, phase-1 sudoers rows, phase-2 status paragraph contradicting
--
135-    test infrastructure); not above 2M/Stage 3.0, which don't touch the
136-    edge.
137:  - D3 bookkeeping drift (structural): consensus two-part fix — D-023
138-    extension (prose status summaries carry an as-of date and defer to
139-    checklist matrix rows; no re-narrated gate lists) + a standing
--
317-   crossover economics kept as Tier-2 (wall meter gate). Dissent: none.
318-
319:4. **Cross-device leaderboard / public model cards — SCOPED to an
320-   internal→public ladder.** Apps position: joules/token next to quality
321-   scores, public leaderboard on identical hardware. Attack (examiner
--
800-| design lens (P2-013) | shared-summary-validator + shared-trace-path designs; B1 "present ≠ non-null" trap; cleanup ownership | shaped 3 consensus items |
801-| examiner lens (P2-013) | **raw-to-trace gap** (biggest catch); durable-evidence condition on A1; historical-corpus non-rewriting policy | major-revision verdict drove real scope change |
802:| planning lens | invariant-shaped commit groups; run_bundle_layout/checklist/council-log bookkeeping omissions; 7-not-6 audit test files; RUN_STATE staleness | beat the lead's grouping |
803-| architect lens | five seams break for Phase 3; three pre-2M contract amendments; composite-reader split note | overturned lead's PP6 |
804-| strategist lens | machine-state lanes ratified; 3.0.1-before-workload-buildout; "feature work stops" carveout; Ed one-pass external push | |
805-| project-examiner lens | detection floor confirmed unowned + concrete gate spec; phase-attribution-below-resolution objection; two-point scaling confound | supplied the "one change" (item 15) |
806-| docs lens | update-ledger scheme; index drift (C-005/C-006 missing — fixed this entry); three named drift items; slimmer M0 | |
807:| attack round (Codex, fresh) | A/B contradiction in lead's synthesis; B2 scope trim; Ed-burden flag; D-030 wording overclaim; 6 code spot-checks all confirmed | ratify-with-changes; all changes accepted |
808-
809-Spend: 8 Codex read-only sessions (~free per economics doctrine); lead
--
814-
815-- Queue: P2-013 re-ranked to 1 (scope grows by raw-to-trace gate +
816:  bookkeeping superset), P2-014 created, lanes annotated, Do-Not-Do-Yet
817-  wording fix — this session.
818-- Decision-log entries land WITH the P2-013/P2-014 implementation (D-011,
--
863-  "my earlier council-log-as-process-history position was too broad
864-  given the duplication evidence." Adopted: run report = the session
865:  record; council log = index rows + genuine-deliberation entries only.
866-- Codex amendments (accepted): bounded waits get a STALLED-handback rule
867-  (never infinite loops); retired ledgers leave a branch/hash pointer.
--
905-carry the full lens tier (folded into multi-stream-worktrees);
906-(3) a volunteered 5.5 addition (vLLM provenance) was rejected at the
907:lead diff gate for hashing fabricated token IDs as realized evidence —
908-first clear model-defect row in the calibration ledger; the correction
909-(node-realized IDs via /tokenize or structured absence) is ledgered
--
1039-
1040-Meta-loop yield note: the invited-peer-design pattern paid again — two
1041:lead designs overturned with strictly better ones (grid, window
1042-packing), consistent with the 2026-07-07 calibration signal that
1043-design-freedom delegation to 5.5 runs hotter than doctrine assumed.
--
1190-  integration-after-clean-oversight (one zero at C-017, C-010 contra),
1191-  Opus-vs-Codex fresh-eyes A/B (sealed same-packet protocol defined; ≥2
1192:  trials before roster change). Prompt-defect class active (~2/large
1193-  session, lead-side); quality denominator (false-positive burden,
1194-  severity mix, triage cost) noted as missing instrumentation (critic 7).
--
1201-  R-016 interim backup becomes serious before 2M.
1202-- CLOSURE: D-013 prose/docstrings back-annotated to marker-bounded
1203:  wording (this batch); C-018 index row added with commit hashes;
1204-  RUN_STATE 734; bank affine-queued line amended. Derivability clean.
1205-- CRITIC dispositions: (1) sealed A/B re-baselining ADOPTED (skill);
--
1438-workflow wrapper agents committed/pushed; lead pathspec commits for
1439-direct codex-run streams. PROCESS DEFECT recorded: the lead ran its
1440:bookkeeping edits concurrently with a workspace-write codex fix round in
1441-the SAME main tree; the fix round's cleanup reverted the uncommitted
1442:bookkeeping (recovered same-session from in-context content) — the
1443:two-writers rule applies to the LEAD as well; bookkeeping waits for tree
1444-quiescence. Dissents: none unresolved.
1445-
--
1512----
1513-
1514:## Index row
1515-
1516:| C-028 | 2026-07-09/11 | C-027 adjudication → integration arc under the Fable-lead / gpt-5.6-sol division of labor (this segment: infrastructure wave + PRs #49/#54/#55 + integration window) | PRs #49, #54, #55 merged mid-arc; held wave #50–#53, #56–#58 integration-reviewed and merged (SHA-guarded) after the integration tree caught 38 cross-stream failures pre-merge; follow-up PR #59 opened from the cross-stream review; refuter tier narrowed 2 blockers via contradictory verdicts; delta re-audits caught 2 fresh blockers in newly-reachable paths; claude-codex-report/v1 + codex-run-v3 + WRITE_SCOPE backstop + NEEDS_RULING adopted (D-064); ~57 recorded Sol invocations |
1517:| C-029 | 2026-07-11/12 | Agent-lane triple (SITE-01 / P2-049 / P2-028): three standard-tier Sol pipelines, per-stream lenses, lead bench adjudication of 5 blocker claims (2 confirmed, 1 partially refuted, 1 design ruling, 1 reproduce-first — refuters replaced by lead code-reading where cheaper); trace + calibration table in `docs/run_reports/2026-07-12-agent-lane-triple.md` §Process Trace Appendix (the ONE home; no full entry here) | PRs #61/#62/#63 opened at lead-gated heads; lead-gate unique catch: fix round's `succeeded`-only rule would refuse legitimate `capped` cells (FIX-14; third "fix rounds introduce defects" datum); implementer caught a stale kernel authority pointer (half-right — lead archaeology completed it, `507f600`); process defects logged: WRITE_SCOPE in-prompt requirement (3 rc=64), unintended ULTRA effort on all 13 invocations (config passthrough; TOOL-01), upstream outage killed 3 delta-audit attempts (re-audits owed pre-merge on #62/#63) |
1518:| C-030 | 2026-07-13 | Restart close (continuation of C-029; Ed-authorized merges): delta re-audits on #62/#63 finals + post-merge integration review, all explicit xhigh (effort fix held: 3 sessions ≈ 7.0M tokens vs the prior 13 ≈ 118M); two lead bench fixes with defect regressions; trace in `docs/run_reports/2026-07-13-restart-merge-deploy.md` (the ONE home; no full entry) | #61-#63 MERGED; delta-audit unique catch DRA-001 (equal-but-malformed identity hashes counted as identity evidence — fourth "fix rounds introduce defects" datum, this one surviving TWO earlier review layers); integration-review unique catch XSI-1 (installed-wheel CI ran only --help; now smokes both new fail-closed surfaces); lead-live layer: deploy ACCEPTED 854,349 B / routes 5/5 / freshness clear + cross-thread breakage fix (P2-028 kernel retirement vs gen_state fidelity tests, caught by the concurrent bridge thread's suite run); concurrent Claude↔Sol bridge landed same tree, lead-verified 8/8 protocol + 4/4 tests before commit; PAUSE: comprehensive whole-project audit declared next gate (Ed) |
1519:| C-031 | 2026-07-13 | Bridge v1 (Ed-directed): 3-round Fable<->Sol design discussion held OVER the MCP bridge itself (thread 019f5a67-00f5); Sol out-designed the lead 3x (hard-block leases vs warn-only, path-level baseline manifests vs status digest, split event logs) — all accepted; 5 draft-choices lead-adjudicated; impl + 2 fix rounds + fresh lens + delta re-audit; full record `docs/run_reports/2026-07-13-bridge-v1.md` (the ONE home) | PR #64 MERGED: bridge-protocol/v1 contract + scripts/bridge (atomic hard-block leases — direct fix for the 2026-07-12 cross-thread collision — baselines, 4-verdict scope-check, thread registry) + adapter FAILED-synthesis; lens caught 4 blockers, delta re-audit caught 1 NEW blocker (malformed-override fail-open; FIFTH fix-rounds-inject-defects datum); audit-loop termination ruling: post-fix2 residue lead-verified directly; suite 1358 OK |
1520-| C-032 | 2026-07-13 | Bridge v1.1 (Ed-directed: "fix up the bridge for maximum co-work"): Sol xhigh design consult over the bridge (thread 019f5d1d-b681-7db1-8714-812fdd2f198b; 5 amendments accepted + v1 duplicate-sentinel adapter bug confirmed); ratified spec Sol-implemented; 3 lenses → 3 fix rounds → 3 delta re-audits, finding convergence 13→6→2→1; full record `docs/run_reports/2026-07-13-bridge-v11.md` (the ONE home; no full entry) | PR #65 MERGED `d285989` (Ed named the merge same session after the harness declined agent self-merge): discussion lane, receipt-anchored session-open/close wrappers (session.lock-serialized, write-only in v1.1), tolerant envelope, per-call reverse effort + echo, peer channels + bounded proposal diffs, one-home effort dedup; delta re-audits caught 6+2+1 fix-round findings (sixth/seventh "fix rounds introduce defects" data) incl. two corrections of the lead; suite 1387 OK; CI green on final head 8b96bd4 |
1521-| C-035 | 2026-07-15 | AXI spec-design phase (Ed: "design as many specs as you can with help from sol"; arc opened post-clearance with predeclared deliverable per WO-022 §5a): three parallel Sol spec pipelines (SA xhigh / SD high / SE xhigh), each author -> fresh counterreview -> fix round(s) -> delta -> lead termination; ~14 Sol sessions ≈ 71.2M tokens (est.); full trace in the 2026-07-14 run report §AXI spec-design phase | Specs landed `1464c93`/`d2bd5ee`/`3b5c4bf`: SA burst-decode contract (implementation-ready; honest frozen-arm goldens after the counterreview refuted byte-identical vs actual code; deterministic anti-top-up ledger), SD pair scorecard (four-option D-016 decision box for Ed; forced-continuation memory probe), SE six AP drafts (estimand demotion on AP-REASON-VARIANCE; union-bound + Markov-quantile floor guards; 21 PROVISIONAL cells with named triggers); 30+ counterreview findings fixed pre-landing; 3 benign lease-close artifacts pending Ed batch adjudication |
1522:| C-034 | 2026-07-14/15 | Audit fix-wave resume + close-out (Ed's AXI handoff §0.2 sequencing; full record `docs/run_reports/2026-07-14-audit-resume-axi.md`, the ONE home): per-order cadence Sol high/xhigh implement → fresh checker → fix rounds → lead gate; 28 Sol sessions ≈ 251M tokens (ARC HARD crossing recorded in the refreshed WO-022 receipt — gate-closing work, policy landed mid-arc); ULTRA comparison audit (intended, pre-declared) + xhigh integration review + Fable completeness critic + C-033 coherence council | S1 closed (WO-010 NEEDS_SCOPE grant, WO-011 checker-FAIL→fix→delta-PASS), S4 closed (WO-019 PASS-0-findings; WO-031 3-major fix round), WO-027 fix round, WO-021 xhigh 3-phase w/ 8a receipt + 4-record-loss BLOCKER migration, WO-022 verbatim landing; integration tree `impl/audit-integration`: 2 unique integration catches (capsule budget union breach; D-068 vacuous-green surfaces) + ULTRA's 2 blockers/20 findings triaged per Ed's substance-over-ceremony ruling (7 fixed `913a2a6`, 4 bench, 5 queued, rest dispositioned §8.5); D-043 closure (17 lines + 6 lead decision-log amendments); critic's 3 gaps closed same session; suite 1532 OK at `f8f0f92`; PR to main awaits Ed's adoption merge; 3 lease adjudications Ed-approved after classifier refused lead self-approval (correctly, all three times) |
1523:| C-033 | 2026-07-14 | AXI intake council (Ed-directed via `docs/axi-handoff.md` + Ed's batched §5 answers this session): short recorded Sol high read-only coherence review of drafted D-066..D-070 (outcomes Ed-directed, not re-decided; consult ran over the audited CLI path because the MCP server is unavailable in this headless session; prompt/response tracked at `docs/process_traces/2026-07-14-c033-axi-consult/`) | Sol verdict DISCUSSION: outcomes authorized, Ed's four D-067 amendments honored; 6 coherence corrections identified and ALL lead-accepted before commit: explicit supersession of the D-058 token-normalization Primary Metric clause (contract text assigned to S-A, keeping S-0 docs-only), dual-basis-capture bundle-state definition (successful idle-eligible request-level; nullable semantics preserved), D-032 gross-only phase semantics named, deploy convention re-attributed C-012→C-013, registry source homes corrected (C5-* bank vs C-023-*/RQ-* registry per D-055), `request_id` pinned to `events.jsonl` `metadata.request_id` with new-version-only reducer dispatch, D-064 duplicate/mismatched index rows cleaned; remaining deploy-instruction surfaces routed to WO-031 + S-0 |
1524:| C-037 | 2026-07-17 | Window-A execution + wrap arc (Ed: floors-first overnight -> advisor deadline -> site rebuild -> exploratory breadth; full records: the two 2026-07-16/17 run reports, the ONE homes): four-failure shakedown story (stale-bundle reuse, wallpaper idle contamination caught by sentinel, 34.6ms trace-boundary bracket via two live-bundle triages, stale-lock exit-0 wart) -> canonical PASS; 248-line/222-bundle floor campaign verified by 8-agent ultracode extraction; advisor brief + README-first site + Learn guide (Ed deployed); exploratory 9-bundle block; DSpark/DFlash feasibility confirmed; D-071..D-075 recorded | PRs #72-#75 merged under D-072 standing authority; delta re-audits caught blockers twice more (10th datum incl. lead-pinned formula defect); fold-in round's refusal caught a forced-report placeholder trace; scope enforcement caught the lead's own stray file (adjudicated benign); floors: request 0.527/0.052 J, phase 1.477/0.786 J, ABBA comparative w/ flagged tail drift; exploratory gross suite: OLMoE ~229 J vs Qwen3-4B ~362.8 J vs 122B ~1072 J (exploratory-labeled) |
1525:| C-036 | 2026-07-16 | Resumption + no-hardware batch (Ed: audits in a workflow + "handle the merge yourself if all is well... get the project ready for my quiet mac"; full record `docs/run_reports/2026-07-16-resumption-nohw-batch.md`, the ONE home): ultracode readiness workflow (4 Sol-high audits + severity-tiered refuters) BEFORE work selection; then 4 streams (SPLIT-AP xhigh contract tier, SITE-02 high standard, AXI-SB xhigh spike, AXI-SD Fable web-verification); every fix round delta-re-audited; three self-merges under Ed's in-session delegation, each with the full D-031-amended gate | PRs #67 (`7593259`, AXI-SA + CI portability fix after the audit caught red CI), #68 (`2778ed2`, SITE-02 — D2 step verified EXECUTED in the CI log), #69 (`9db4546`, SPLIT-AP freeze) merged; integration review 0 cross-stream defects, merged main 1630 OK; kernel closures 51→48 IDs; AXI-SB live probes (lead-run, B∈{2,4}) → verdict `supported`, Mac C5-2.2 leg mint staged on `impl/axi-sb` (effective on its merge); delta re-audit caught a LEAD-pinned predictor defect (8th fix-rounds-inject-defects datum, first lead-authored); AXI-SD memo: OLMo pair d_active 0.0016 + 8GB-fit may moot Option A's premise, Qwen3 pair confirmed-fails G10 (17.17 GB) |
1526-| C-039 | 2026-07-28 | Mint-implementation session (Ed: resume per RUN_STATE, then "merge on green + start the mint consult"; magistrate topology; full record `docs/run_reports/2026-07-28-floor-mint-implementation.md`, the ONE home): PR #87 gauntlet (2 Sol xhigh lenses + 5 Sol high refuters + 1 Opus contract refuter, lieutenant-directed), E4 fix + CLEAN delta re-audit, D-081 parser ruling (Ed, async question), Sol xhigh mint design consult (3 DISAGREEs sustained -> D-082), 7-stage xhigh implementation, suite-pruning consult (0 removals clear D-061) | PR #87 MERGED `058c918`; `impl/mint-tool` pushed unmerged (review owed); C1 SPLIT (Sol nit vs Opus should-fix) magistrate-synthesized to should-fix, closed via ratified Q4; 5 broken-wake incidents -> tracked-poll pattern folded to codex-delegation; lieutenant self-flagged 2 retracted fabricated verdict narrations (mechanism removed); concurrent-session force-push anomaly flagged to Ed; **ADDENDUM at the end of this file** records the 2026-07-29/30 continuation (FIX-6..9 gauntlet, three cold gates with paired Opus contract-lens refuters, mint #1, the 7B floor window; rulings D-083..D-088; D-088 recorded in the same-day close-out); **ADDENDUM II** records the 2026-07-30/31 escalation consults (cooldown-join design consult → D5-J/D-089; contrast-window recovery consult, the first trigger firing inside a measurement window) |
1527-
--
1545-refuter, auditor, and design consultant across ~57 recorded
1546-invocations. The lead retained worktree/merge authority, every final
1547:diff gate, all live verification, and bookkeeping.
1548-
1549-Scope of this segment: PR #49 (NV-GATE-2 code-now + flake
--
1584-- **Sol merge review:** caught the lead's own merge-resolution
1585-  error — the branch's updated P2-005 row silently lost by a
1586:  whole-file `--theirs` checkout during the #49 conflict
1587-  resolution; repaired as a proper 3-way merge (`13f6c9e`). Only
1588-  layer to catch it.
--
1616-  false-positive firings tuned same-day; NEEDS_SCOPE compliant
1617-  stops ×3 (p2037 fix round, doc008 ×2) — each returning the
1618:  correct paths where the lead had guessed wrong.
1619-
1620-Scope enforcement fired in production: two sessions (p2043-impl,
--
1656-- **codex-run-v3** — append-only event-stream manifest
1657-  (run_started/run_finished/run_consumed), retry-with-resume,
1658:  lead-authored recovery rows on wrapper failure.
1659-- **WRITE_SCOPE backstop** — post-run diff vs declared scope; exit
1660-  77 + evidence bundle on violation; NEEDS_SCOPE prospective-only
--
1684-read-only Sol lenses over a shared packet → 8 xhigh refuter verdicts,
1685-blockers 2 refuters with distinct lenses); Sol xhigh round-8b fix wave under
1686:enforced WRITE_SCOPE (one NEEDS_SCOPE early-return, lead-ruled, fixture fix
1687-applied at the bench); bounded 8b delta re-audit; lead full-suite gates
1688-(2081 → 2088 passed, 0 failures); commit `040ca3a`; round-9 FINAL
--
1711-(route: keep refuter briefs mechanism-neutral); (2) lead bench-edited the
1712-worktree while an enforced-scope Sol session ran in it → false
1713:SCOPE_VIOLATION attribution + resume-registry loss (rule: no lead edits in
1714-a tree with a live enforced-scope session); (3) the known xhigh review-genre
1715-null-final-message mode recurred on round 9; the documented bridge-resume
--
1830-pre-audit wave, fold, fold2 and run-book sessions brings the day's Sol
1831-total to ~15. Four Opus agents: three contract/design refuters (~96k /
1832:120k / 144k tokens) plus one dictated-fills drafting/verification agent
1833-(~115k) — the latter caught five material errors in the lead's own
1834:dictation of this entry, including the effort-tier discrepancy ruled on
1835-below. Lead orchestration on top. The
1836-`codex-usage` ledger reads all zeros for the 5h and 24h windows ("local
--
1847-blocker-refuter shape; memory and skills to be updated by the lead.
1848-
1849:Dissent recorded: on F4 the lead overrode the contract refuter's
1850-downgrade and kept blocker priority, on the grounds that the
1851-anchor-fallback replay path was about to be exercised by the next
--
1900-primary delegated lieutenant, Fable is consulted when genuinely needed,
1901-Sol remains the execution workhorse, and the lead adjudicates rather
1902:than performing the labor. The standing dictate is recorded in the
1903-`instrument-mix-authority` memory and in the ledger §2 — this entry is
1904-the first session run under it.
--
1973-  quiet-window dominance, with a stop-loss and a heartbeat that checks
1974-  for an in-flight measurement before acting; **R3** premise labeling.
1975:  It identified failure modes the lead's own rules missed — notably
1976-  that **more wakeups can contaminate a live measurement**. It
1977-  recommended **no demotion**, explicitly arguing against its own
--
1979-  the same wake semantics.
1980-- **Lead (Opus 5) bench catches:** detected that its own suite
1981:  verification was **worthless because it piped output through `tail`**,
1982-  which discarded the summary line and masked the real exit code behind
1983-  tail's; **adjudicated Sol's blocker to L1 by reading the primary
--
1991-  and comparative **before either reviewer reported**.
1992-
1993:### Lead errors (recorded plainly)
1994-
1995-1. **The lost quiet window — the most expensive process error of the
--
2042-  `runs_window_b_20260726_bound/neg8-drift-bound.json`, fields
2043-  `single_member_endpoint_bound_j` and `replicated_endpoint_bound_j`;
2044:  the lead's dictation called the latter the "triplet mean").
2045-  **The whole-window verdict was still running when this entry was
2046-  written and is recorded as PENDING. No result is asserted here.**
--
2084-  seconds, and it **overturned the lead's own conclusion** about the
2085-  lead's own failure, produced a better-shaped rule set than the lead
2086:  had drafted, found failure modes the lead missed, and declined its own
2087-  promotion. The generalizable shape is that the question had already
2088-  been assembled — Fable did no retrieval, only judgment.
--
2095-  wider, and it gained its first executable demonstration.**
2096-
2097:### Dictated-fact verification notes
2098-
2099:This entry was written from lead dictation and verified against primary
2100:evidence. Two dictated line numbers were **off and are corrected above**:
2101-the anchor-ceiling gate is at `joulewise/uncertainty_evidence.py:367`
2102:(dictated `:366`, which is the offset-envelope computation), and the
2103-unconditional `limited_without_admin` assignment is at
2104-`joulewise/environment.py:908` inside `_probe_clock_sync` at l.904
2105:(dictated `:904`). Two dictated facts could **not** be corroborated in
2106-the surviving tree and are recorded as **lead-reported**: the
2107-**5.544 ms** slew instance (no `wall_minus_monotonic_span_s` above
--
2118-## C-039 addendum: the FIX-6..9 gauntlet, three cold gates, and the 7B floor window (2026-07-29/30)
2119-
2120:Continuation of the C-039 index row above, covering the arc that carried
2121-`impl/mint-tool` from `f63a334` to `969a4d6` plus mint #1 and the
2122-`window_7bfloor_20260729` collection. Rulings from this arc are D-083..D-088 (D-088 in the same-day close-out);
--
2260-## C-039 addendum II: two escalation consults — the cooldown-join design consult and the contrast-window recovery (2026-07-30/31)
2261-
2262:Second continuation of the C-039 index row. Both entries here are **consults
2263-convened because an escalation trigger fired**, not council rounds convened by
2264-ritual — one on a code defect class, one live inside a measurement window. The
--
2276-
2277-**Layer:** Sol xhigh design consult, thread `019fb5c8…3937`,
2278:codex-adjudicated with lead replays, question scoped to *where
2279-declaration-completeness is enforced* (the ONE home).
2280-
--
2555-  registered.
2556-- Magistrate: Variant D synthesis; two packet-hygiene failures recorded
2557:  against itself (the Option C runway line; the selective quotation);
2558-  cold-gate packet authorship moved to MECHANICAL assembly permanently.
2559-
--
2648-the structural cardinality/capacity finding — the cross-model pairing
2649-earned its keep again (a fresh Fable shares the magistrate's own
2650:dispositions). Packet hygiene: the refuter recorded FOUR findings against
2651-the magistrate's gate-3 packet (selective clause-7 quotation omitting the
2652-half that decided the gate; flags not quoted in full incl. the blocking
--
2754-in-flight 7B-mint license neither in-session consultant could see);
2755-lead bench — two fix commits, clause-(d) re-record, byte-identical
2756:pinned replay, exit-status-masking recurrence self-caught. Fix rounds
2757-introduced defects twice more (data #11, #12). Both gauntlets held;
2758-the deviation escape and rule-11 gates fired as designed; the night's
--
2772-effort cap held — no xhigh anywhere this arc) → Sol HIGH enforced-scope
2773-implementation → lead bench diff-read + full-suite replay ON THE
2774:INTEGRATION TREE (2487 OK, exit-0 unpiped) → fresh Sol HIGH delta
2775-re-audit → bench hardening from the auditor's specified fix shape →
2776-merge-ref CI green. Merge itself: harness classifier denies agent
--
2784-rendered-signature pin (guard passed while the core's is-None load
2785-path was defeated), plus the remerge-tree fidelity proof and the
2786:loader-mutation kill of the new regression. LEAD BENCH — the piped
2787:exit-status recurrence self-caught AGAIN (third occurrence; the unpiped
2788:re-run is now reflex, the habit clearly is not), stale RUN_STATE
2789-claims (char captures "collected" that never ran; F1's byte-frozen
2790-framing in active restart text). CI — remains the only layer that

exec
/bin/zsh -lc "rg -n -i -C 2 'index' docs/council_log.md | sed -n '1,240p'" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
39-standing instructions.
40-
41:## Index
42-
43-| ID | Date | Topic | Outcome |
--
804-| strategist lens | machine-state lanes ratified; 3.0.1-before-workload-buildout; "feature work stops" carveout; Ed one-pass external push | |
805-| project-examiner lens | detection floor confirmed unowned + concrete gate spec; phase-attribution-below-resolution objection; two-point scaling confound | supplied the "one change" (item 15) |
806:| docs lens | update-ledger scheme; index drift (C-005/C-006 missing — fixed this entry); three named drift items; slimmer M0 | |
807-| attack round (Codex, fresh) | A/B contradiction in lead's synthesis; B2 scope trim; Ed-burden flag; D-030 wording overclaim; 6 code spot-checks all confirmed | ratify-with-changes; all changes accepted |
808-
--
863-  "my earlier council-log-as-process-history position was too broad
864-  given the duplication evidence." Adopted: run report = the session
865:  record; council log = index rows + genuine-deliberation entries only.
866-- Codex amendments (accepted): bounded waits get a STALLED-handback rule
867-  (never infinite loops); retired ledgers leave a branch/hash pointer.
--
1012-arithmetic (n=5 resolves ~1.5-1.8x CV), C5-1.1 between-model df
1013-insufficiency, rank-gap rule, binomial energy/correct guard;
1014:consumers — Q4-Q6 had NO Phase 4 figure/claims-index consumers, P2-010
1015-substrate/ladder split, energy_token_j over-promotion under config
1016-denominators; scout — phase-gross vs idle-subtracted headline mixing,
--
1201-  R-016 interim backup becomes serious before 2M.
1202-- CLOSURE: D-013 prose/docstrings back-annotated to marker-bounded
1203:  wording (this batch); C-018 index row added with commit hashes;
1204-  RUN_STATE 734; bank affine-queued line amended. Derivability clean.
1205-- CRITIC dispositions: (1) sealed A/B re-baselining ADOPTED (skill);
--
1435-operation-loop §4a) ran on P2-030 — 5.5's design memo ratified with pins
1436-before implementation; zero design rework followed. Codex worktree
1437:commits remain sandbox-blocked (index.lock) despite git permissions —
1438-workflow wrapper agents committed/pushed; lead pathspec commits for
1439-direct codex-run streams. PROCESS DEFECT recorded: the lead ran its
--
1512----
1513-
1514:## Index row
1515-
1516-| C-028 | 2026-07-09/11 | C-027 adjudication → integration arc under the Fable-lead / gpt-5.6-sol division of labor (this segment: infrastructure wave + PRs #49/#54/#55 + integration window) | PRs #49, #54, #55 merged mid-arc; held wave #50–#53, #56–#58 integration-reviewed and merged (SHA-guarded) after the integration tree caught 38 cross-stream failures pre-merge; follow-up PR #59 opened from the cross-stream review; refuter tier narrowed 2 blockers via contradictory verdicts; delta re-audits caught 2 fresh blockers in newly-reachable paths; claude-codex-report/v1 + codex-run-v3 + WRITE_SCOPE backstop + NEEDS_RULING adopted (D-064); ~57 recorded Sol invocations |
--
1521-| C-035 | 2026-07-15 | AXI spec-design phase (Ed: "design as many specs as you can with help from sol"; arc opened post-clearance with predeclared deliverable per WO-022 §5a): three parallel Sol spec pipelines (SA xhigh / SD high / SE xhigh), each author -> fresh counterreview -> fix round(s) -> delta -> lead termination; ~14 Sol sessions ≈ 71.2M tokens (est.); full trace in the 2026-07-14 run report §AXI spec-design phase | Specs landed `1464c93`/`d2bd5ee`/`3b5c4bf`: SA burst-decode contract (implementation-ready; honest frozen-arm goldens after the counterreview refuted byte-identical vs actual code; deterministic anti-top-up ledger), SD pair scorecard (four-option D-016 decision box for Ed; forced-continuation memory probe), SE six AP drafts (estimand demotion on AP-REASON-VARIANCE; union-bound + Markov-quantile floor guards; 21 PROVISIONAL cells with named triggers); 30+ counterreview findings fixed pre-landing; 3 benign lease-close artifacts pending Ed batch adjudication |
1522-| C-034 | 2026-07-14/15 | Audit fix-wave resume + close-out (Ed's AXI handoff §0.2 sequencing; full record `docs/run_reports/2026-07-14-audit-resume-axi.md`, the ONE home): per-order cadence Sol high/xhigh implement → fresh checker → fix rounds → lead gate; 28 Sol sessions ≈ 251M tokens (ARC HARD crossing recorded in the refreshed WO-022 receipt — gate-closing work, policy landed mid-arc); ULTRA comparison audit (intended, pre-declared) + xhigh integration review + Fable completeness critic + C-033 coherence council | S1 closed (WO-010 NEEDS_SCOPE grant, WO-011 checker-FAIL→fix→delta-PASS), S4 closed (WO-019 PASS-0-findings; WO-031 3-major fix round), WO-027 fix round, WO-021 xhigh 3-phase w/ 8a receipt + 4-record-loss BLOCKER migration, WO-022 verbatim landing; integration tree `impl/audit-integration`: 2 unique integration catches (capsule budget union breach; D-068 vacuous-green surfaces) + ULTRA's 2 blockers/20 findings triaged per Ed's substance-over-ceremony ruling (7 fixed `913a2a6`, 4 bench, 5 queued, rest dispositioned §8.5); D-043 closure (17 lines + 6 lead decision-log amendments); critic's 3 gaps closed same session; suite 1532 OK at `f8f0f92`; PR to main awaits Ed's adoption merge; 3 lease adjudications Ed-approved after classifier refused lead self-approval (correctly, all three times) |
1523:| C-033 | 2026-07-14 | AXI intake council (Ed-directed via `docs/axi-handoff.md` + Ed's batched §5 answers this session): short recorded Sol high read-only coherence review of drafted D-066..D-070 (outcomes Ed-directed, not re-decided; consult ran over the audited CLI path because the MCP server is unavailable in this headless session; prompt/response tracked at `docs/process_traces/2026-07-14-c033-axi-consult/`) | Sol verdict DISCUSSION: outcomes authorized, Ed's four D-067 amendments honored; 6 coherence corrections identified and ALL lead-accepted before commit: explicit supersession of the D-058 token-normalization Primary Metric clause (contract text assigned to S-A, keeping S-0 docs-only), dual-basis-capture bundle-state definition (successful idle-eligible request-level; nullable semantics preserved), D-032 gross-only phase semantics named, deploy convention re-attributed C-012→C-013, registry source homes corrected (C5-* bank vs C-023-*/RQ-* registry per D-055), `request_id` pinned to `events.jsonl` `metadata.request_id` with new-version-only reducer dispatch, D-064 duplicate/mismatched index rows cleaned; remaining deploy-instruction surfaces routed to WO-031 + S-0 |
1524-| C-037 | 2026-07-17 | Window-A execution + wrap arc (Ed: floors-first overnight -> advisor deadline -> site rebuild -> exploratory breadth; full records: the two 2026-07-16/17 run reports, the ONE homes): four-failure shakedown story (stale-bundle reuse, wallpaper idle contamination caught by sentinel, 34.6ms trace-boundary bracket via two live-bundle triages, stale-lock exit-0 wart) -> canonical PASS; 248-line/222-bundle floor campaign verified by 8-agent ultracode extraction; advisor brief + README-first site + Learn guide (Ed deployed); exploratory 9-bundle block; DSpark/DFlash feasibility confirmed; D-071..D-075 recorded | PRs #72-#75 merged under D-072 standing authority; delta re-audits caught blockers twice more (10th datum incl. lead-pinned formula defect); fold-in round's refusal caught a forced-report placeholder trace; scope enforcement caught the lead's own stray file (adjudicated benign); floors: request 0.527/0.052 J, phase 1.477/0.786 J, ABBA comparative w/ flagged tail drift; exploratory gross suite: OLMoE ~229 J vs Qwen3-4B ~362.8 J vs 122B ~1072 J (exploratory-labeled) |
1525-| C-036 | 2026-07-16 | Resumption + no-hardware batch (Ed: audits in a workflow + "handle the merge yourself if all is well... get the project ready for my quiet mac"; full record `docs/run_reports/2026-07-16-resumption-nohw-batch.md`, the ONE home): ultracode readiness workflow (4 Sol-high audits + severity-tiered refuters) BEFORE work selection; then 4 streams (SPLIT-AP xhigh contract tier, SITE-02 high standard, AXI-SB xhigh spike, AXI-SD Fable web-verification); every fix round delta-re-audited; three self-merges under Ed's in-session delegation, each with the full D-031-amended gate | PRs #67 (`7593259`, AXI-SA + CI portability fix after the audit caught red CI), #68 (`2778ed2`, SITE-02 — D2 step verified EXECUTED in the CI log), #69 (`9db4546`, SPLIT-AP freeze) merged; integration review 0 cross-stream defects, merged main 1630 OK; kernel closures 51→48 IDs; AXI-SB live probes (lead-run, B∈{2,4}) → verdict `supported`, Mac C5-2.2 leg mint staged on `impl/axi-sb` (effective on its merge); delta re-audit caught a LEAD-pinned predictor defect (8th fix-rounds-inject-defects datum, first lead-authored); AXI-SD memo: OLMo pair d_active 0.0016 + 8GB-fit may moot Option A's premise, Qwen3 pair confirmed-fails G10 (17.17 GB) |
--
2118-## C-039 addendum: the FIX-6..9 gauntlet, three cold gates, and the 7B floor window (2026-07-29/30)
2119-
2120:Continuation of the C-039 index row above, covering the arc that carried
2121-`impl/mint-tool` from `f63a334` to `969a4d6` plus mint #1 and the
2122-`window_7bfloor_20260729` collection. Rulings from this arc are D-083..D-088 (D-088 in the same-day close-out);
--
2144-  within-member duplicate into one candidate."* A member declaring
2145-  `bundle_ids: ["x", "x"]` with only one usable `physical_members` row for
2146:  `x` yields a single candidate with identity `(manifest, member_index, -1)`;
2147-  the one-row fast path then accepts its cooldown evidence **without ever
2148-  invoking the supersession matcher**. The `-1` guard prevents a *valid*
--
2260-## C-039 addendum II: two escalation consults — the cooldown-join design consult and the contrast-window recovery (2026-07-30/31)
2261-
2262:Second continuation of the C-039 index row. Both entries here are **consults
2263-convened because an escalation trigger fired**, not council rounds convened by
2264-ritual — one on a code defect class, one live inside a measurement window. The
--
2336-  remediator sweep** — modules run sequentially, so clearing one says nothing
2337-  about the next. The sweep ran to 05:31Z; a second, unrelated intruder
2338:  (`corespotlightd` at 624 CPU ms/s, Spotlight indexing the fresh bundles) was
2339-  then also waited out, and round 3 launched only after a full-sweep
2340-  completion, **eight consecutive daemon-quiet minutes past the Time Machine

exec
/bin/zsh -lc "rg -n -i -C 1 'spend:|rough spend|total spend|≈ [0-9.]+M tokens|~[0-9]+ Sol|tokens /|sessions ≈|invocations|hours|hour|minute|~free|accounting_unknown|zeros for the 5h' docs/council_log.md" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
61-| C-020 | 2026-07-08 | STOP-AND-ANALYZE WHOLE PROJECT: technical + research merit debate (full entry below) — 69-agent Codex assessment workflow + 2 independent Fable position papers + recorded Fable-vs-Codex debate; owner-directed | Merit verdict recorded (docs/reviews/2026-07-08-technical-merit-review.md); D-048 model-first split program + D-049 transfer-boundary accounting promoted; question ranking adjudicated (Q4→Q1 coupled #1, Token-Shape Null sustained #2, Q6 elevated #3, affine ladder = validity instrument); crossover prior corrected by arithmetic; cheap-validity priority set (bundle publication + external re-reduction first); repo-verified gaps: bundles unpublished, no LICENSE, D-033 strict-validation legacy bypass |
62:| C-019 | 2026-07-08 | Post-suite-build meta-reassessment (full entry below) — 4 analyst lanes (5.5-direction study over 43 invocations; calibration longitudinal; project status/value ranking; closure) + completeness critic | Direction doctrine folded into codex-delegation skill (precedence/autonomy/FIX-N/production-gate clauses; model-version scoping rule pre-upgrade); D-013 prose back-annotated marker-bounded; shakedown gate added to P2-015; P2-025 adjacency + P1-008 elevation (incl. examiner acceptance-bar ask); pre-#21 corpus validity noted (dict-read-scale overhead, no re-reduction); watch items: integration-after-oversight, Opus A/B |
63-| C-018 | 2026-07-08 | D-013 alignment-capture window fix (parallel session; full entry below) | sampling_stopped stamped before alignment capture (PR #21: `255a7e6`, bookkeeping `c2e51b2`, merge `49c5b66`); suite 734; D-013 prose back-annotated to marker-bounded wording in the reassessment batch |
--
71-| C-027 | 2026-07-09 | Whole-project council review with gpt-5.6-sol xhigh (first production session; 7 lenses: topdocs/rigor/stats/meta/reverse/arch/negspace + counterreview + independent Fable-tier final examiner; full record `docs/reviews/2026-07-09-c027-whole-project-review.md`) | 8 blocker clusters confirmed (token-denominator mislabel, superseded D-053 prose, RUN_STATE dual next-action, claim machinery unimplemented+unowned, empty D-050 manifest, four D-031 direct-to-main commits, evidence-integrity trio, protocol blockers); claim surfaces corrected same session; 14 follow-up queue rows + NV-GATE-2 additions to P2-005; D-060 proposed + D-061..D-063 accepted; counterreview reversed the lead twice (legacy-gate framing, restructure staging) |
72:| C-038 | 2026-07-25/26 | FLOOR-LABEL-01 gauntlet close (D-078 cl.11 labelled attribution-limited floors) + quiet-window collection; Ed re-proportioned the instrument mix mid-session (Opus 5 subagents = primary delegated lieutenant, Fable on genuine need, Sol = execution workhorse, lead adjudicates); full entry below | Opus-contract lens verdict COMPARATIVE COVERAGE: COMPLETE with 4 should-fix / 4 nits, incl. the `_combined_floor` key-sniffing misattribution mirrored bug-for-bug into `artifact.py` (so validation recomputes the same wrong answer and ships) and the ratio-unit floor/diagnostic inversion; Sol xhigh audit's 1 blocker (runnable V3 probe: comparative blocks minted WITHOUT admissible half-widths validate clean, floor_gate 5e-324 J vs 2.6484 J) ADJUDICATED DOWN to registered limitation L1 — first concrete demonstration of L1, and FLOOR-LABEL-01 recorded as modestly WIDENING its blast radius; Sol xhigh clock diagnosis root-caused window C to transient wall-vs-monotonic slew over the 5 ms ceiling (7.769 ms verified) and corrected the lead's duration hypothesis; Fable adjudication (zero tool uses, 108 s) OVERTURNED the lead's own self-diagnosis and named the disposition (rigorous on work products, exempts its own premises about the environment) → rules R1/R2/R3, no demotion; window B 59/59 clean (whole-window verdict PENDING), window C failed twice on clock slew, window D not started; FIVE lead errors recorded, incl. the ~10-hour lost quiet window (untracked `nohup` + turn ended with no wake source) and TWO exit-status masking incidents → generalization: EXIT STATUS IS NOT EVIDENCE OF WORK DONE |
73-| C-040 | 2026-08-01/02 | Commit-3 cooldown-join gauntlet: five fix rounds and three cold-gate dispositions | PR #93 merged after the custody micro-commit and exact-set pin; D-105 recorded the residual recognizer boundary; every review layer produced unique catches |
--
163-  Opus ground truth: detection floor (idle stddev 5.4 W > mean 3.5 W),
164:  ~30-75 bundles/hour throughput with automation (not schema) as the
165-  campaign blocker, `SummaryMetrics.uncertainty` is a documented-but-DEAD
--
172-- Resolutions: promote Q4-Q6; queue D-014 implementation as the highest
173:  credibility-per-hour item; question bank doc created.
174-
--
376-   prescribe the rescue design (paired ABBA/interleaved runs, n=10-20
377:   for ~1% effects — cheap on this instrument at 30-75 bundles/hour).
378-   Outcome: affected Tier-1 questions carry an explicit "requires
--
460-  Codex rounds were spent.
461:- Spend: 5 Codex lens invocations + orchestrator grounding/synthesis;
462-  no repo mutations (session shape B honored).
--
566-- Fresh-eyes Codex counterreview lenses: 2 unique (K-1, K-2) + 6 robustness
567:  (K-5, K-6). ~free (Codex quota).
568-- Fable orchestrator diff gates: 1 unique (K-3). Orchestrator context.
--
593-6. Explicit `model:` on every orchestrator spawn (I-2) (multi-stream).
594:7. Fleet health checks from outside evidence, on landing or ~hourly (I-3)
595-   (multi-stream).
--
808-
809:Spend: 8 Codex read-only sessions (~free per economics doctrine); lead
810-context spent on briefs, adjudication, and this record. Zero-unique-catch
--
1065-markers, MLX memory snapshots, sampler-availability metadata) spawned
1066:the window-a-capture worktree stream the same hour — the class of
1067-finding that had to precede the 2M corpus' birth.
--
1176-Lane findings adopted:
1177:- 5.5-DIRECTION STUDY (priority lane, 43 invocations deep-sampled):
1178-  direction doctrine distilled and FOLDED into the codex-delegation
--
1515-
1516:| C-028 | 2026-07-09/11 | C-027 adjudication → integration arc under the Fable-lead / gpt-5.6-sol division of labor (this segment: infrastructure wave + PRs #49/#54/#55 + integration window) | PRs #49, #54, #55 merged mid-arc; held wave #50–#53, #56–#58 integration-reviewed and merged (SHA-guarded) after the integration tree caught 38 cross-stream failures pre-merge; follow-up PR #59 opened from the cross-stream review; refuter tier narrowed 2 blockers via contradictory verdicts; delta re-audits caught 2 fresh blockers in newly-reachable paths; claude-codex-report/v1 + codex-run-v3 + WRITE_SCOPE backstop + NEEDS_RULING adopted (D-064); ~57 recorded Sol invocations |
1517:| C-029 | 2026-07-11/12 | Agent-lane triple (SITE-01 / P2-049 / P2-028): three standard-tier Sol pipelines, per-stream lenses, lead bench adjudication of 5 blocker claims (2 confirmed, 1 partially refuted, 1 design ruling, 1 reproduce-first — refuters replaced by lead code-reading where cheaper); trace + calibration table in `docs/run_reports/2026-07-12-agent-lane-triple.md` §Process Trace Appendix (the ONE home; no full entry here) | PRs #61/#62/#63 opened at lead-gated heads; lead-gate unique catch: fix round's `succeeded`-only rule would refuse legitimate `capped` cells (FIX-14; third "fix rounds introduce defects" datum); implementer caught a stale kernel authority pointer (half-right — lead archaeology completed it, `507f600`); process defects logged: WRITE_SCOPE in-prompt requirement (3 rc=64), unintended ULTRA effort on all 13 invocations (config passthrough; TOOL-01), upstream outage killed 3 delta-audit attempts (re-audits owed pre-merge on #62/#63) |
1518:| C-030 | 2026-07-13 | Restart close (continuation of C-029; Ed-authorized merges): delta re-audits on #62/#63 finals + post-merge integration review, all explicit xhigh (effort fix held: 3 sessions ≈ 7.0M tokens vs the prior 13 ≈ 118M); two lead bench fixes with defect regressions; trace in `docs/run_reports/2026-07-13-restart-merge-deploy.md` (the ONE home; no full entry) | #61-#63 MERGED; delta-audit unique catch DRA-001 (equal-but-malformed identity hashes counted as identity evidence — fourth "fix rounds introduce defects" datum, this one surviving TWO earlier review layers); integration-review unique catch XSI-1 (installed-wheel CI ran only --help; now smokes both new fail-closed surfaces); lead-live layer: deploy ACCEPTED 854,349 B / routes 5/5 / freshness clear + cross-thread breakage fix (P2-028 kernel retirement vs gen_state fidelity tests, caught by the concurrent bridge thread's suite run); concurrent Claude↔Sol bridge landed same tree, lead-verified 8/8 protocol + 4/4 tests before commit; PAUSE: comprehensive whole-project audit declared next gate (Ed) |
1519-| C-031 | 2026-07-13 | Bridge v1 (Ed-directed): 3-round Fable<->Sol design discussion held OVER the MCP bridge itself (thread 019f5a67-00f5); Sol out-designed the lead 3x (hard-block leases vs warn-only, path-level baseline manifests vs status digest, split event logs) — all accepted; 5 draft-choices lead-adjudicated; impl + 2 fix rounds + fresh lens + delta re-audit; full record `docs/run_reports/2026-07-13-bridge-v1.md` (the ONE home) | PR #64 MERGED: bridge-protocol/v1 contract + scripts/bridge (atomic hard-block leases — direct fix for the 2026-07-12 cross-thread collision — baselines, 4-verdict scope-check, thread registry) + adapter FAILED-synthesis; lens caught 4 blockers, delta re-audit caught 1 NEW blocker (malformed-override fail-open; FIFTH fix-rounds-inject-defects datum); audit-loop termination ruling: post-fix2 residue lead-verified directly; suite 1358 OK |
1520-| C-032 | 2026-07-13 | Bridge v1.1 (Ed-directed: "fix up the bridge for maximum co-work"): Sol xhigh design consult over the bridge (thread 019f5d1d-b681-7db1-8714-812fdd2f198b; 5 amendments accepted + v1 duplicate-sentinel adapter bug confirmed); ratified spec Sol-implemented; 3 lenses → 3 fix rounds → 3 delta re-audits, finding convergence 13→6→2→1; full record `docs/run_reports/2026-07-13-bridge-v11.md` (the ONE home; no full entry) | PR #65 MERGED `d285989` (Ed named the merge same session after the harness declined agent self-merge): discussion lane, receipt-anchored session-open/close wrappers (session.lock-serialized, write-only in v1.1), tolerant envelope, per-call reverse effort + echo, peer channels + bounded proposal diffs, one-home effort dedup; delta re-audits caught 6+2+1 fix-round findings (sixth/seventh "fix rounds introduce defects" data) incl. two corrections of the lead; suite 1387 OK; CI green on final head 8b96bd4 |
1521:| C-035 | 2026-07-15 | AXI spec-design phase (Ed: "design as many specs as you can with help from sol"; arc opened post-clearance with predeclared deliverable per WO-022 §5a): three parallel Sol spec pipelines (SA xhigh / SD high / SE xhigh), each author -> fresh counterreview -> fix round(s) -> delta -> lead termination; ~14 Sol sessions ≈ 71.2M tokens (est.); full trace in the 2026-07-14 run report §AXI spec-design phase | Specs landed `1464c93`/`d2bd5ee`/`3b5c4bf`: SA burst-decode contract (implementation-ready; honest frozen-arm goldens after the counterreview refuted byte-identical vs actual code; deterministic anti-top-up ledger), SD pair scorecard (four-option D-016 decision box for Ed; forced-continuation memory probe), SE six AP drafts (estimand demotion on AP-REASON-VARIANCE; union-bound + Markov-quantile floor guards; 21 PROVISIONAL cells with named triggers); 30+ counterreview findings fixed pre-landing; 3 benign lease-close artifacts pending Ed batch adjudication |
1522:| C-034 | 2026-07-14/15 | Audit fix-wave resume + close-out (Ed's AXI handoff §0.2 sequencing; full record `docs/run_reports/2026-07-14-audit-resume-axi.md`, the ONE home): per-order cadence Sol high/xhigh implement → fresh checker → fix rounds → lead gate; 28 Sol sessions ≈ 251M tokens (ARC HARD crossing recorded in the refreshed WO-022 receipt — gate-closing work, policy landed mid-arc); ULTRA comparison audit (intended, pre-declared) + xhigh integration review + Fable completeness critic + C-033 coherence council | S1 closed (WO-010 NEEDS_SCOPE grant, WO-011 checker-FAIL→fix→delta-PASS), S4 closed (WO-019 PASS-0-findings; WO-031 3-major fix round), WO-027 fix round, WO-021 xhigh 3-phase w/ 8a receipt + 4-record-loss BLOCKER migration, WO-022 verbatim landing; integration tree `impl/audit-integration`: 2 unique integration catches (capsule budget union breach; D-068 vacuous-green surfaces) + ULTRA's 2 blockers/20 findings triaged per Ed's substance-over-ceremony ruling (7 fixed `913a2a6`, 4 bench, 5 queued, rest dispositioned §8.5); D-043 closure (17 lines + 6 lead decision-log amendments); critic's 3 gaps closed same session; suite 1532 OK at `f8f0f92`; PR to main awaits Ed's adoption merge; 3 lease adjudications Ed-approved after classifier refused lead self-approval (correctly, all three times) |
1523-| C-033 | 2026-07-14 | AXI intake council (Ed-directed via `docs/axi-handoff.md` + Ed's batched §5 answers this session): short recorded Sol high read-only coherence review of drafted D-066..D-070 (outcomes Ed-directed, not re-decided; consult ran over the audited CLI path because the MCP server is unavailable in this headless session; prompt/response tracked at `docs/process_traces/2026-07-14-c033-axi-consult/`) | Sol verdict DISCUSSION: outcomes authorized, Ed's four D-067 amendments honored; 6 coherence corrections identified and ALL lead-accepted before commit: explicit supersession of the D-058 token-normalization Primary Metric clause (contract text assigned to S-A, keeping S-0 docs-only), dual-basis-capture bundle-state definition (successful idle-eligible request-level; nullable semantics preserved), D-032 gross-only phase semantics named, deploy convention re-attributed C-012→C-013, registry source homes corrected (C5-* bank vs C-023-*/RQ-* registry per D-055), `request_id` pinned to `events.jsonl` `metadata.request_id` with new-version-only reducer dispatch, D-064 duplicate/mismatched index rows cleaned; remaining deploy-instruction surfaces routed to WO-031 + S-0 |
--
1545-refuter, auditor, and design consultant across ~57 recorded
1546:invocations. The lead retained worktree/merge authority, every final
1547-diff gate, all live verification, and bookkeeping.
--
1626-
1627:Rough spend (from the two manifests + local usage accounting;
1628:estimates, not billing truth): 2 ultra sessions ≈ 100M tokens
1629-(p2041-vetted composition, P2-037 engine); 53 recorded xhigh
1630:invocations (14 v2-manifest + 37 v3-event-stream + 2 transition-era
1631:rows) — local 24h accounting shows 50 xhigh sessions ≈ 171M tokens;
1632-2 high (both FAILED rc=1 resume attempts, work recovered in later
--
1638-window, arc-close truth for the table above; estimates, not billing):
1639:59 Sol sessions / 330.6M tokens / ~17.5h session time — xhigh 55 ≈
1640-190.4M, ultra 2 ≈ 100.3M, high 2 ≈ 40.0M (both FAILED). Composition
--
1824-
1825:Rough spend (estimates, not billing truth): the gauntlet proper (audit
1826:round 1 onward) recorded 11 distinct Sol wrapper invocations — 4 audits
1827-(3 xhigh, 1 high), 2 execution refuters (both high), 3 implementation
--
1835-below. Lead orchestration on top. The
1836:`codex-usage` ledger reads all zeros for the 5h and 24h windows ("local
1837-quota signal unavailable in referenced session logs") — the feed is
--
1965-  rule was *not* the right generalization, because with a working wake
1966:  mechanism the information-block would have cost **17 minutes** — the
1967:  10-hour loss is fully explained mechanically, not by a missing
1968-  deadline policy. It then named the underlying disposition: **the lead
--
1998-   turn "holding until the diagnosis lands". No wake could fire. The
1999:   Mac never slept (`pmset -g log`), and **~10 hours of open quiet
2000-   window were lost** — enough for both remaining collection windows.
--
2006-   wrong — but the lead's *certainty* was unwarranted either way.
2007:4. **Three failed `codex-run-v3` invocations** from guessing at the
2008-   interface instead of reading the error. The actual cause: the
--
2055-
2056:### Rough spend (estimates, not billing truth)
2057-
2058-Four delegated calls carry figures: the Opus 5 contract lens ~164k
2059:tokens / 50 tool uses / ~11 min; the Fable adjudication 21k tokens /
2060-**zero tool uses** / 108 s; the Sol xhigh independent audit ~23 min and
--
2063-recorded). Lead orchestration, the bench catches, and all live
2064:verification on top. Three additional `codex-run-v3` invocations failed
2065-outright on the `WRITE_SCOPE` JSON defect (error 4) and a fourth did no
--
2212-events** (macOS's malware scanner, then a second, unidentified CPU
2213:excursion — the operator log records only an hourly-snapshot *hypothesis*
2214-for it) that the admission gates caught and that the protocol recovered from per its own written
--
2339-  then also waited out, and round 3 launched only after a full-sweep
2340:  completion, **eight consecutive daemon-quiet minutes past the Time Machine
2341:  hour boundary**, and a clean final `powermetrics` tasks sample.
2342-- **Continuation chain-shape verification.** The consult verified the round-3
--
2356-code defect, and of a consult being convened at a stage boundary by a solo
2357:operator under quiet-lock. The cost was one consult against a ~2.6-hour window
2358-that would otherwise have been re-run on a third guess; the mechanism should be
--
2406-through to a clean salvage close. The consult cost one bounded session
2407:against an 11-hour runway that two more blind aborts would have burned.
2408-
--
2513-C3-RECOGNIZER-EXACT-01 under D-105's compensating controls (custody
2514:sidecar; writer-side key assertion). Total spend: ~6 Sol implementation
2515:sessions, 6 independent audits, 3 cold-gate pairs, across ~20 hours of
2516-the Ed-authorized runway — the most heavily reviewed change in the
--
2799-
2800:Session: Fable magistrate, Ed's 12-hour autonomous window (directive
2801-batch 2026-08-05 ~22:00: effort cap lifted, fast tier specified,

exec
/bin/zsh -lc 'git status --short --branch' in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 53ms:
## main...origin/main

codex
# Council-log meta-audit

Read-only audit completed; the worktree remains clean.

## Counting method

A “catch” is one independently named defect, defect class, or decision-invalidating finding attributed to a layer. I excluded clean verification, duplicated rediscovery, design recommendations without an identified failure, and refuter suppressions/repricings from the catch total. Those suppressions are reported separately.

The log changes granularity over time: some entries say `~20`, `10+`, or `~60`. Accordingly, `≥` is the auditable minimum, not false precision. `U` means severity unstated.

## 1. Unique layer yield

| Layer | Unique catches | Severity where stated | Main evidence |
|---|---:|---|---|
| Pre-decision consult | **42** | **4 blocker, 38 U** | Bridge/design consults and coherence review in [C-031–C-033](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk/docs/council_log.md:1519>); three mint disagreements in [C-039](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk/docs/council_log.md:1526>); escalation/window consults in [C-039 addenda II–III](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk/docs/council_log.md:2260>); CAL-BRACKET’s three blockers in [C-041](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk/docs/council_log.md:2599>); four packet corrections in [C-042](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk/docs/council_log.md:2686>); [C-044](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk/docs/council_log.md:1724>), [C-048](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk/docs/council_log.md:2763>), [C-049](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk/docs/council_log.md:2798>). |
| Implementation-audit lenses | **≥153** | Directly allocable: **13 blocker, 30 should-fix, 7 nit, 3 medium/major, ≥93 U**; C-045’s seven blocker-tier claims span initial/delta rounds and cannot be cleanly split | Ten findings in [C-001](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk/docs/council_log.md:86>); ten in [C-006](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk/docs/council_log.md:507>); `~20` unit-lens plus one major in [C-017](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk/docs/council_log.md:1105>); ten final-head catches in C-022 and four in C-026, recorded in the [index](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk/docs/council_log.md:65>); 30+ in [C-035](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk/docs/council_log.md:1521>); ten in [C-038](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk/docs/council_log.md:1906>); initial rounds in [C-040](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk/docs/council_log.md:2416>), [C-043](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk/docs/council_log.md:1680>), [C-045](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk/docs/council_log.md:1742>), and [C-047](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk/docs/council_log.md:2740>). |
| Delta re-audit | **57** | **17 blocker, 8 should-fix, 1 nit, 31 U** | Five in [C-028](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk/docs/council_log.md:1532>); 1/1/9 in C-030/31/32 [index rows](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk/docs/council_log.md:1518>); six in C-043; four in [C-039 addendum](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk/docs/council_log.md:2139>); twelve in C-040; one in the [C-040 addendum](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk/docs/council_log.md:2520>); three in C-041; one in C-048; three in C-049. |
| Cold gate, excluding its paired refuter | **11** | **5 blocker, 6 U** | Two packet/phase catches plus two successor blockers in [C-039 addendum](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk/docs/council_log.md:2139>); four across C-040’s three gates; three in C-047; issuance F1/F2 in [C-049](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk/docs/council_log.md:2828>). |
| Refuter pairs | **40 catches** plus **≥20 explicit suppressions/repricings** | **6 blocker, 34 U** among catches | Two narrowed blockers in C-028; C-045’s contract/execution adjacencies and triage in [C-045](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk/docs/council_log.md:1742>); two ruling-level catches in C-039; twelve across C-040’s first three gates; five in C-040 addendum; eleven across C-041 gates 2/3 and packet hygiene; four in C-047. The suppression count includes ten findings killed in C-025, four killed/narrowed/split in C-043, and six repriced/rejected in C-045. |
| Lead bench/live gate | **15** | **2 blocker, 1 should-fix, 12 U** | Three in C-006; fabricated-evidence blocker in C-010; three live-only catches in C-017; prompt defect in C-022; FIX-14 in C-029; cross-thread state break in C-030; exit-status catch in C-038; recurrence in C-047; exit-status plus two stale claims in [C-048](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk/docs/council_log.md:2779>). Pure live confirmations, such as C-028’s arithmetic/doctor checks, were not counted. |
| CI | **1** | **1 U** | C-022’s merge-ref-only fixtures × strict-rules interaction, in the [index](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk/docs/council_log.md:66>). Green verdicts and “only layer structurally able to see merge ref” assertions are verification, not catches. |
| Integration review/tree | **48** | **2 should-fix, 46 U** | Two in C-006; five seam drifts in C-024; 38 combined-head failures in C-028; XSI-1 in C-030; two integration catches in C-034. Explicit zeroes: C-017 and C-036. |
| Oversight/prune lens | **≥112** | **10 blocker, ≥102 U** | `10+` pre-merge oversight findings in C-017; C-027’s eight blocker clusters, `~60` accepted lens findings, and eight examiner rescues in [C-027](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk/docs/council_log.md:1447>); 20 ULTRA findings plus three critic gaps in C-034; RT-1 from the concurrent sweep in C-047; two explicit oversight/prune findings in C-049. The C-039 suite-pruning consult yielded zero removals. |

The strongest numerically recorded defect-catching layers are implementation audit, oversight, delta re-audit, integration, and refuter pairs. The most important qualitative distinction is that refuters contribute materially beyond their 40 catches: their ≥20 suppressions/repricings prevented severity inflation and bad fixes.

## 2. Spend signals

- Early councils were effectively unmetered: C-005 records five Codex lenses; C-007 records eight read-only sessions, both described as approximately free under the then-current quota doctrine ([C-005 spend](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk/docs/council_log.md:451>), [C-007 spend](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk/docs/council_log.md:796>)).

- C-028 is the anti-example: **59 Sol sessions, 330.6M tokens, ~17.5 hours, ~$1,050 combined estimated cost**, with a ~$2,300 non-manifest upper bound. Sol produced ~180× the token volume, but Fable was ~3.4× the estimated cost because cache reads dominated ([C-028 spend](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk/docs/council_log.md:1627>)).

- The clearest effort-control experiment is C-029→C-030: accidental ULTRA consumed **~118M tokens over 13 invocations**; corrected explicit xhigh consumed **~7.0M over three sessions** while still producing DRA-001 and XSI-1—roughly a 17× aggregate-token reduction ([C-029/C-030](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk/docs/council_log.md:1517>)).

- C-034 crossed the arc HARD band: **28 Sol sessions, ~251M tokens**. C-035 then used **~14 sessions, ~71.2M tokens** for three spec pipelines ([C-034/C-035](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk/docs/council_log.md:1521>)).

- C-045 used **11 distinct Sol wrapper invocations** for the gauntlet, ~15 for the day, plus four Opus agents totaling roughly **475k tokens**. Its usage feed returned zeros and was explicitly recorded as unavailable, not zero spend ([C-045 spend](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk/docs/council_log.md:1824>)).

- C-038 provides the best model-allocation micro-signal: Opus contract lens **164k tokens / 11 min**; Fable adjudication **21k / 108 seconds / zero tool uses**; Sol audit and diagnosis **23 + 17 minutes**. The tiny, pre-assembled Fable judgment consult overturned the lead more cheaply than another retrieval-heavy pass ([C-038 spend](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk/docs/council_log.md:2056>)).

- C-040 spent **~6 implementation sessions + 6 audits + 3 cold-gate pairs across ~20 hours**. Expensive, but every layer caught something and the refuter amended all three gates ([C-040 outcome](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk/docs/council_log.md:2501>)).

- In-window consults appear highly leveraged: one bounded consult protected a **~2.6-hour** window; another cost one session against an **11-hour** runway ([C-039 addenda](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk/docs/council_log.md:2356>)).

## 3. Zero-yield streaks and drop candidates

There is **no currently eligible automatic drop candidate**.

The old C-006 rule—two zero-catch sessions—was superseded by D-061: three mechanically applicable exposures trigger an expected-loss review, never automatic deletion; safety, final-head, and integration layers are protected.

Observed streaks:

- **CI:** at least three recent green applicable exposures without a unique catch—C-046, C-048, C-049. It is not drop-eligible: CI is a low-token structural merge-ref oracle, and C-022 records the one interaction no other layer could see.

- **Cold Fable instance:** had a temporary zero-unique streak in the C-040 addendum/C-041 gates, where the paired refuter supplied the decisive findings. C-047 reset that streak with three unique catches.

- **Integration review:** C-036 was explicitly zero, but the log does not establish two later mechanically applicable independent integration-review exposures. C-048 used an integration tree as a lead gate, not a separate integration review.

- **Suite-pruning lens:** one zero-yield exposure in C-039 only—insufficient.

- The original generic Opus refuter/verifier was already dropped under the old rule at C-006. That is not evidence against the later **distinct contract + execution refuter pair**, which is one of the highest-yield instruments.

## 4. Recurring lead error classes

Counts below are atomic incidents where the log supports them; `≥` reflects plural or approximate source language.

| Lead-error habit | Count | Evidence |
|---|---:|---|
| Piped suite exit status masking | **3** | First `tail` masking in C-038, recurrence in C-047, explicitly called the **third occurrence** in C-048. |
| Other exit-0/non-result confusion | **2 additional** | C-037 stale-lock exit-0 wart; C-038 wrapper returned zero for a read-only session that did no work. |
| Stale `RUN_STATE` claims | **4 atomic claims across 3 entries** | C-007 general staleness; C-027 dual next-action; C-048’s two stale active claims. |
| Council/index-row drift | **≥5 row defects across 4 entries** | Missing C-005/C-006 rows in C-007; missing C-018 row in C-019; duplicate/mismatched D-064 rows in C-033; C-046 required retrospective reconstruction. |
| Packet/evidence/dictation hygiene | **≥19 atomic errors across 5 entries** | Five dictated-entry errors in C-045; four C-038 verification discrepancies; two C-040-addendum packet failures; four repeated packet-hygiene findings in C-041; four packet/counter errors in C-042. |
| Live-tree/two-writer violations | **3** | Same-main-tree bookkeeping/fix collision in C-025; installed-runner edit during a live run in C-028; lead bench edit during enforced scope in C-043. |
| Scope/interface launch mistakes | **11** | Three lead-guessed scope misses in C-028; three `WRITE_SCOPE` rc=64 launches in C-029; three invalid-JSON launches plus one missing sandbox in C-038; one lead stray file in C-037. |
| Lead-authored bad pins/formulations | **≥10** | Two bad wire pins in C-010; prompt defect in C-022; merge-resolution loss in C-028; two lead corrections in C-032; predictor pin in C-036; formula pin in C-037; two fatigued candidate formulations rejected in C-040. |
| Wake-source/tracked-poll failures | **6 incidents across C-038/C-039** | One ~10-hour lost quiet window plus five later broken-wake incidents. |
| Merge/base-resolution mistakes | **2** | C-017 wrong stacked-base target; C-028 whole-file `--theirs` lost the P2-005 update. |

The clearest “habit has not stuck” signals are exit-status discipline, packet factual hygiene, state/index bookkeeping, scope-launch preparation, and exclusive tree ownership. Each recurred after an explicit corrective doctrine had already been recorded.

## 5. Recommendations ranked by expected catch-per-token

1. **Install one mechanical lead-closeout preflight.** Highest expected return because it spends almost no model tokens and attacks the densest recurring classes. It should refuse completion unless: suite execution is unpiped with its own summary; delegated envelopes report actual completion; `RUN_STATE` active claims and council index rows reconcile; no second writer owns the tree; quoted gate clauses/flags are complete; and declared scope parses before launch. The named-failure bar is amply met by the counts above.

2. **Keep fresh delta re-audit after every fix, but default it to bounded HIGH with changed-path/reachability probes.** It produced **57 catches, including 17 stated blockers**. C-048 showed HIGH still found a live blocker on a 127-line mostly-test change, while C-029→C-030 demonstrates the enormous token penalty of accidental high effort. Escalate only on repeated signature or decision ambiguity.

3. **Retain the distinct contract + execution refuter pair only for blocker/cold-gate findings, with runnable probes required.** It supplied **40 catches plus ≥20 suppressions/repricings**, and repeatedly outperformed same-family agreement. C-045 showed HIGH refuters were sufficient; C-040/C-041 showed the pairing—not an additional homogeneous reviewer—is what corrected adjudicator/cold-instance convergence. Batch should-fixes and nits without refuters.

Bottom line: spend less on broad homogeneous audit volume and more on three narrow instruments—mechanical lead hygiene, fresh post-fix re-audit, and probe-bearing cross-model refutation. CI stays as cheap structural insurance, not as a defect-discovery layer.
tokens used
155,419
# Council-log meta-audit

Read-only audit completed; the worktree remains clean.

## Counting method

A “catch” is one independently named defect, defect class, or decision-invalidating finding attributed to a layer. I excluded clean verification, duplicated rediscovery, design recommendations without an identified failure, and refuter suppressions/repricings from the catch total. Those suppressions are reported separately.

The log changes granularity over time: some entries say `~20`, `10+`, or `~60`. Accordingly, `≥` is the auditable minimum, not false precision. `U` means severity unstated.

## 1. Unique layer yield

| Layer | Unique catches | Severity where stated | Main evidence |
|---|---:|---|---|
| Pre-decision consult | **42** | **4 blocker, 38 U** | Bridge/design consults and coherence review in [C-031–C-033](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk/docs/council_log.md:1519>); three mint disagreements in [C-039](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk/docs/council_log.md:1526>); escalation/window consults in [C-039 addenda II–III](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk/docs/council_log.md:2260>); CAL-BRACKET’s three blockers in [C-041](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk/docs/council_log.md:2599>); four packet corrections in [C-042](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk/docs/council_log.md:2686>); [C-044](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk/docs/council_log.md:1724>), [C-048](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk/docs/council_log.md:2763>), [C-049](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk/docs/council_log.md:2798>). |
| Implementation-audit lenses | **≥153** | Directly allocable: **13 blocker, 30 should-fix, 7 nit, 3 medium/major, ≥93 U**; C-045’s seven blocker-tier claims span initial/delta rounds and cannot be cleanly split | Ten findings in [C-001](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk/docs/council_log.md:86>); ten in [C-006](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk/docs/council_log.md:507>); `~20` unit-lens plus one major in [C-017](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk/docs/council_log.md:1105>); ten final-head catches in C-022 and four in C-026, recorded in the [index](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk/docs/council_log.md:65>); 30+ in [C-035](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk/docs/council_log.md:1521>); ten in [C-038](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk/docs/council_log.md:1906>); initial rounds in [C-040](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk/docs/council_log.md:2416>), [C-043](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk/docs/council_log.md:1680>), [C-045](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk/docs/council_log.md:1742>), and [C-047](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk/docs/council_log.md:2740>). |
| Delta re-audit | **57** | **17 blocker, 8 should-fix, 1 nit, 31 U** | Five in [C-028](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk/docs/council_log.md:1532>); 1/1/9 in C-030/31/32 [index rows](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk/docs/council_log.md:1518>); six in C-043; four in [C-039 addendum](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk/docs/council_log.md:2139>); twelve in C-040; one in the [C-040 addendum](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk/docs/council_log.md:2520>); three in C-041; one in C-048; three in C-049. |
| Cold gate, excluding its paired refuter | **11** | **5 blocker, 6 U** | Two packet/phase catches plus two successor blockers in [C-039 addendum](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk/docs/council_log.md:2139>); four across C-040’s three gates; three in C-047; issuance F1/F2 in [C-049](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk/docs/council_log.md:2828>). |
| Refuter pairs | **40 catches** plus **≥20 explicit suppressions/repricings** | **6 blocker, 34 U** among catches | Two narrowed blockers in C-028; C-045’s contract/execution adjacencies and triage in [C-045](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk/docs/council_log.md:1742>); two ruling-level catches in C-039; twelve across C-040’s first three gates; five in C-040 addendum; eleven across C-041 gates 2/3 and packet hygiene; four in C-047. The suppression count includes ten findings killed in C-025, four killed/narrowed/split in C-043, and six repriced/rejected in C-045. |
| Lead bench/live gate | **15** | **2 blocker, 1 should-fix, 12 U** | Three in C-006; fabricated-evidence blocker in C-010; three live-only catches in C-017; prompt defect in C-022; FIX-14 in C-029; cross-thread state break in C-030; exit-status catch in C-038; recurrence in C-047; exit-status plus two stale claims in [C-048](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk/docs/council_log.md:2779>). Pure live confirmations, such as C-028’s arithmetic/doctor checks, were not counted. |
| CI | **1** | **1 U** | C-022’s merge-ref-only fixtures × strict-rules interaction, in the [index](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk/docs/council_log.md:66>). Green verdicts and “only layer structurally able to see merge ref” assertions are verification, not catches. |
| Integration review/tree | **48** | **2 should-fix, 46 U** | Two in C-006; five seam drifts in C-024; 38 combined-head failures in C-028; XSI-1 in C-030; two integration catches in C-034. Explicit zeroes: C-017 and C-036. |
| Oversight/prune lens | **≥112** | **10 blocker, ≥102 U** | `10+` pre-merge oversight findings in C-017; C-027’s eight blocker clusters, `~60` accepted lens findings, and eight examiner rescues in [C-027](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk/docs/council_log.md:1447>); 20 ULTRA findings plus three critic gaps in C-034; RT-1 from the concurrent sweep in C-047; two explicit oversight/prune findings in C-049. The C-039 suite-pruning consult yielded zero removals. |

The strongest numerically recorded defect-catching layers are implementation audit, oversight, delta re-audit, integration, and refuter pairs. The most important qualitative distinction is that refuters contribute materially beyond their 40 catches: their ≥20 suppressions/repricings prevented severity inflation and bad fixes.

## 2. Spend signals

- Early councils were effectively unmetered: C-005 records five Codex lenses; C-007 records eight read-only sessions, both described as approximately free under the then-current quota doctrine ([C-005 spend](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk/docs/council_log.md:451>), [C-007 spend](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk/docs/council_log.md:796>)).

- C-028 is the anti-example: **59 Sol sessions, 330.6M tokens, ~17.5 hours, ~$1,050 combined estimated cost**, with a ~$2,300 non-manifest upper bound. Sol produced ~180× the token volume, but Fable was ~3.4× the estimated cost because cache reads dominated ([C-028 spend](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk/docs/council_log.md:1627>)).

- The clearest effort-control experiment is C-029→C-030: accidental ULTRA consumed **~118M tokens over 13 invocations**; corrected explicit xhigh consumed **~7.0M over three sessions** while still producing DRA-001 and XSI-1—roughly a 17× aggregate-token reduction ([C-029/C-030](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk/docs/council_log.md:1517>)).

- C-034 crossed the arc HARD band: **28 Sol sessions, ~251M tokens**. C-035 then used **~14 sessions, ~71.2M tokens** for three spec pipelines ([C-034/C-035](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk/docs/council_log.md:1521>)).

- C-045 used **11 distinct Sol wrapper invocations** for the gauntlet, ~15 for the day, plus four Opus agents totaling roughly **475k tokens**. Its usage feed returned zeros and was explicitly recorded as unavailable, not zero spend ([C-045 spend](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk/docs/council_log.md:1824>)).

- C-038 provides the best model-allocation micro-signal: Opus contract lens **164k tokens / 11 min**; Fable adjudication **21k / 108 seconds / zero tool uses**; Sol audit and diagnosis **23 + 17 minutes**. The tiny, pre-assembled Fable judgment consult overturned the lead more cheaply than another retrieval-heavy pass ([C-038 spend](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk/docs/council_log.md:2056>)).

- C-040 spent **~6 implementation sessions + 6 audits + 3 cold-gate pairs across ~20 hours**. Expensive, but every layer caught something and the refuter amended all three gates ([C-040 outcome](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk/docs/council_log.md:2501>)).

- In-window consults appear highly leveraged: one bounded consult protected a **~2.6-hour** window; another cost one session against an **11-hour** runway ([C-039 addenda](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk/docs/council_log.md:2356>)).

## 3. Zero-yield streaks and drop candidates

There is **no currently eligible automatic drop candidate**.

The old C-006 rule—two zero-catch sessions—was superseded by D-061: three mechanically applicable exposures trigger an expected-loss review, never automatic deletion; safety, final-head, and integration layers are protected.

Observed streaks:

- **CI:** at least three recent green applicable exposures without a unique catch—C-046, C-048, C-049. It is not drop-eligible: CI is a low-token structural merge-ref oracle, and C-022 records the one interaction no other layer could see.

- **Cold Fable instance:** had a temporary zero-unique streak in the C-040 addendum/C-041 gates, where the paired refuter supplied the decisive findings. C-047 reset that streak with three unique catches.

- **Integration review:** C-036 was explicitly zero, but the log does not establish two later mechanically applicable independent integration-review exposures. C-048 used an integration tree as a lead gate, not a separate integration review.

- **Suite-pruning lens:** one zero-yield exposure in C-039 only—insufficient.

- The original generic Opus refuter/verifier was already dropped under the old rule at C-006. That is not evidence against the later **distinct contract + execution refuter pair**, which is one of the highest-yield instruments.

## 4. Recurring lead error classes

Counts below are atomic incidents where the log supports them; `≥` reflects plural or approximate source language.

| Lead-error habit | Count | Evidence |
|---|---:|---|
| Piped suite exit status masking | **3** | First `tail` masking in C-038, recurrence in C-047, explicitly called the **third occurrence** in C-048. |
| Other exit-0/non-result confusion | **2 additional** | C-037 stale-lock exit-0 wart; C-038 wrapper returned zero for a read-only session that did no work. |
| Stale `RUN_STATE` claims | **4 atomic claims across 3 entries** | C-007 general staleness; C-027 dual next-action; C-048’s two stale active claims. |
| Council/index-row drift | **≥5 row defects across 4 entries** | Missing C-005/C-006 rows in C-007; missing C-018 row in C-019; duplicate/mismatched D-064 rows in C-033; C-046 required retrospective reconstruction. |
| Packet/evidence/dictation hygiene | **≥19 atomic errors across 5 entries** | Five dictated-entry errors in C-045; four C-038 verification discrepancies; two C-040-addendum packet failures; four repeated packet-hygiene findings in C-041; four packet/counter errors in C-042. |
| Live-tree/two-writer violations | **3** | Same-main-tree bookkeeping/fix collision in C-025; installed-runner edit during a live run in C-028; lead bench edit during enforced scope in C-043. |
| Scope/interface launch mistakes | **11** | Three lead-guessed scope misses in C-028; three `WRITE_SCOPE` rc=64 launches in C-029; three invalid-JSON launches plus one missing sandbox in C-038; one lead stray file in C-037. |
| Lead-authored bad pins/formulations | **≥10** | Two bad wire pins in C-010; prompt defect in C-022; merge-resolution loss in C-028; two lead corrections in C-032; predictor pin in C-036; formula pin in C-037; two fatigued candidate formulations rejected in C-040. |
| Wake-source/tracked-poll failures | **6 incidents across C-038/C-039** | One ~10-hour lost quiet window plus five later broken-wake incidents. |
| Merge/base-resolution mistakes | **2** | C-017 wrong stacked-base target; C-028 whole-file `--theirs` lost the P2-005 update. |

The clearest “habit has not stuck” signals are exit-status discipline, packet factual hygiene, state/index bookkeeping, scope-launch preparation, and exclusive tree ownership. Each recurred after an explicit corrective doctrine had already been recorded.

## 5. Recommendations ranked by expected catch-per-token

1. **Install one mechanical lead-closeout preflight.** Highest expected return because it spends almost no model tokens and attacks the densest recurring classes. It should refuse completion unless: suite execution is unpiped with its own summary; delegated envelopes report actual completion; `RUN_STATE` active claims and council index rows reconcile; no second writer owns the tree; quoted gate clauses/flags are complete; and declared scope parses before launch. The named-failure bar is amply met by the counts above.

2. **Keep fresh delta re-audit after every fix, but default it to bounded HIGH with changed-path/reachability probes.** It produced **57 catches, including 17 stated blockers**. C-048 showed HIGH still found a live blocker on a 127-line mostly-test change, while C-029→C-030 demonstrates the enormous token penalty of accidental high effort. Escalate only on repeated signature or decision ambiguity.

3. **Retain the distinct contract + execution refuter pair only for blocker/cold-gate findings, with runnable probes required.** It supplied **40 catches plus ≥20 suppressions/repricings**, and repeatedly outperformed same-family agreement. C-045 showed HIGH refuters were sufficient; C-040/C-041 showed the pairing—not an additional homogeneous reviewer—is what corrected adjudicator/cold-instance convergence. Batch should-fixes and nits without refuters.

Bottom line: spend less on broad homogeneous audit volume and more on three narrow instruments—mechanical lead hygiene, fresh post-fix re-audit, and probe-bearing cross-model refutation. CI stays as cheap structural insurance, not as a defect-discovery layer.
