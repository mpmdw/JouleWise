Reading additional input from stdin...
OpenAI Codex v0.146.1
--------
workdir: /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u3
model: gpt-5.6-sol
provider: openai
approval: never
sandbox: workspace-write [workdir, /tmp, $TMPDIR]
reasoning effort: xhigh
reasoning summaries: none
session id: 019fdde3-ba95-7be2-87f6-8bd98a1f05a3
--------
user
DELTA RE-AUDIT of U3 fix round 2 (read-only; write no files; FINAL MESSAGE in neutral engineering language, conclusions only, no code quotes beyond file:line, no attack phrasing). Branch impl/d117-u3-pinset-v2 at HEAD. History: an audit found postcollection custody pins were self-attested; fix round 1 added evidence inputs but the delta found the class SURVIVING as 'presence-only authentication'; fix round 2 (FIX-1b) claims every pinned custody field now has a named equality check against supplied authenticated evidence, plus FIX-6b (three-way six-decimal / full-precision / extraction-report consistency with a coordinated-inconsistency regression) and FIX-8 (production-CLI authentication path test, implementation-independent golden fixture). Records at origin/main: docs/process_traces/2026-08-07-d117-u-units/U3-*.
CHARGE — this is the SECOND attempt on the authentication class, and a third survival fires an escalation trigger (the next spend becomes a design consult, not another fix round). Answer precisely:
(1) For EACH pinned custody field (each receipt id, each content digest, bracket-binding hash, terminal ledger head, extraction-report hash, observed drift, applied allowance): is the pinned value now COMPARED FOR EQUALITY against a value read out of the supplied evidence artifact, or is it still only checked for presence/shape? Answer per field.
(2) Reproduce the original scenario: replace the custody hashes with values that disagree with the evidence, adjust drift and allowance, repair the pinset's own self-hashes — does the mint now refuse, and with a per-field named reason?
(3) What authenticates the EVIDENCE ARTIFACTS themselves? If the evidence is operator-supplied and unauthenticated, the equality checks move the trust boundary rather than closing it — say so plainly if true.
(4) FIX-6b: can a coordinated change to BOTH the report and the pin still pass? FIX-8: does the production-CLI test exercise the real entry point?
(5) SAME-SIGNATURE STATEMENT: does the self-attestation/presence-only class survive in ANY form — yes/no, with support.
Run the focused suite, the v1 parity suite and the shared-caller set; report exact tails. CLEAN needs a checks-performed line.
codex
I’ll perform a read-only delta audit at the requested HEAD, trace every custody field from supplied evidence through the mint refusal path, then run the focused, v1-parity, and shared-caller suites and capture their exact tails. I will not modify any files.
exec
/bin/zsh -lc "pwd && rg --files -g 'AGENTS.md' -g 'RUN_STATE.md' -g 'TASK_QUEUE.md' -g 'AGENT_PLAN.md' -g 'docs/agent_playbook.md' -g 'docs/orchestration.md' -g 'docs/contracts/bridge_protocol.md' -g 'docs/process_traces/2026-08-07-d117-u-units/U3-*' | sort && git status --short --branch && git log -5 --oneline --decorate" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u3
 succeeded in 0ms:
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u3
AGENTS.md
AGENT_PLAN.md
RUN_STATE.md
TASK_QUEUE.md
docs/agent_playbook.md
docs/contracts/bridge_protocol.md
docs/orchestration.md
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-CONTRACT.md
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-EXEC.md
docs/process_traces/2026-08-07-d117-u-units/U3-FIX-CONTRACT.md
site_capsule/AGENTS.md
## impl/d117-u3-pinset-v2...origin/impl/d117-u3-pinset-v2
454f777 (HEAD -> impl/d117-u3-pinset-v2, origin/impl/d117-u3-pinset-v2) U3 FIX-1b/6b/8: authenticated postcollection pins (named equality check per custody field against supplied evidence — presence no longer satisfies a pin), three-way six-decimal/full-precision/report consistency with the coordinated-inconsistency regression, production-CLI authentication path test, implementation-independent golden fixture
dea7c87 Merge main (D-117 index fix) into U3 branch
1a4511e U3: pinset v2 + four-cell generalized mint, through fix round 1 (authenticated postcollection pins; no internal literal derivation; D-082 consumption-semantics pin; bound inventory fields; aggregate-cell allowlist consistency; full-precision pins; strict allowance-count; independent golden fixtures)
0d9392f U1 delta verdict custodied: 7/8 closed, issued-prefix intact; FIX-6 recovery-boundary blocker -> FIX-6b (pinned idempotent shape) with binding no-round-three stop-condition; classifier-block recovery noted
4628fa0 U1 paired audits custodied (3 BLOCKERs: L5 binding optional, D-109 universe deletion, torn-tail ledger; 2 HIGH live-proofs) + lead FIX contract

exec
/bin/zsh -lc "rg -n '"'^#|''^##|ACTIVE_STOP_CARD|Current Project Status|Known Workspace State|What Is Next'"' RUN_STATE.md TASK_QUEUE.md docs/agent_playbook.md docs/orchestration.md AGENT_PLAN.md docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-CONTRACT.md docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-EXEC.md docs/process_traces/2026-08-07-d117-u-units/U3-FIX-CONTRACT.md" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u3
 succeeded in 0ms:
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
docs/orchestration.md:1:# The Orchestration Process
docs/orchestration.md:12:## Roles: a lead, independent implementers/reviewers, and a human at the top
docs/orchestration.md:45:## The loop, end to end
docs/orchestration.md:110:### Stop cards and paused work
docs/orchestration.md:113:updates an `ACTIVE_STOP_CARD` at the top of `RUN_STATE.md`. While active,
docs/orchestration.md:142:## The artifact system (where rigor becomes auditable)
docs/orchestration.md:189:## Council discipline
docs/orchestration.md:210:## Spend guardrails (WO-022; R2 ruled, Ed-ratified 2026-07-13)
docs/orchestration.md:261:## Topology: how it evolved (an example of the loop improving itself)
docs/orchestration.md:288:## What one session looks like (2026-07-07/08, the merge session)
docs/orchestration.md:306:## Reconstructing the loop on a clean machine
docs/orchestration.md:338:## Where to read the evidence
docs/agent_playbook.md:1:# Agent Playbook: Ordered Missions
docs/agent_playbook.md:24:## How To Pick A Mission
docs/agent_playbook.md:50:## Mission M0: Preflight (every session)
docs/agent_playbook.md:52:1. Read only the targeted `RUN_STATE.md` sections: `ACTIVE_STOP_CARD`
docs/agent_playbook.md:53:   if present, "Current Project Status", "Known Workspace State", and
docs/agent_playbook.md:54:   "What Is Next". If the stop card is ACTIVE, it overrides this
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
RUN_STATE.md:206:#104 registration batch, #106 ledger-bootstrap infra, #107 QUIET-GUARD
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
RUN_STATE.md:2008:12. If an `ACTIVE_STOP_CARD` exists below, it overrides every normal
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
RUN_STATE.md:2358:#59 integration-review fixes and the #60 DOC-008 kernel refresh); none
RUN_STATE.md:2381:## Session History (pointers only — run reports own the narrative)
RUN_STATE.md:2503:## Current Verification
RUN_STATE.md:2600:### Historical verification archive (exact at the recorded heads)
RUN_STATE.md:2743:## Known Workspace State
RUN_STATE.md:2810:## Historical Next-Work Snapshot (superseded 2026-07-15)
RUN_STATE.md:2828:## Reference Decisions And Blockers (non-selection context)
TASK_QUEUE.md:1:# JouleWise Task Queue
TASK_QUEUE.md:6:## Intake Rule For New Tasks
TASK_QUEUE.md:15:6. If `RUN_STATE.md` contains an ACTIVE `ACTIVE_STOP_CARD`, that card
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
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-EXEC.md:18:/bin/zsh -lc 'git status --short --branch && rg -n "''^(#|##|###) |ACTIVE_STOP_CARD|Current Project Status|Known Workspace State|What Is Next" RUN_STATE.md && rg -n "''^(#|##|###) |Current Queue|Do-Not-Do-Yet" TASK_QUEUE.md && sed -n '"'1,240p' docs/agent_playbook.md && sed -n '1,260p' docs/orchestration.md" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u3
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-EXEC.md:20:## impl/d117-u3-pinset-v2...origin/main [behind 13]
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-EXEC.md:69:2004:12. If an `ACTIVE_STOP_CARD` exists below, it overrides every normal
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-EXEC.md:71:2039:## ACTIVE_STOP_CARD
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-EXEC.md:81:2178:## Current Project Status
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-EXEC.md:91:2739:## Known Workspace State
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-EXEC.md:113:# Agent Playbook: Ordered Missions
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-EXEC.md:136:## How To Pick A Mission
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-EXEC.md:162:## Mission M0: Preflight (every session)
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-EXEC.md:164:1. Read only the targeted `RUN_STATE.md` sections: `ACTIVE_STOP_CARD`
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-EXEC.md:165:   if present, "Current Project Status", "Known Workspace State", and
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-EXEC.md:166:   "What Is Next". If the stop card is ACTIVE, it overrides this
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-EXEC.md:203:## Mission M1: Slice 2N — Pre-Hardware Hardening (queue P2-007)
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-EXEC.md:233:### 2N.1 `RunContext` seam + raw evidence
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-EXEC.md:255:### 2N.2 Measured window excludes sampler startup
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-EXEC.md:274:### 2N.3 Reducer token-count fallback
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-EXEC.md:290:### 2N.4 Rail-summation timestamp contract
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-EXEC.md:305:### 2N.5 Config schema accepts emitted configs
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-EXEC.md:324:### 2N.6 Post-hoc `reduce` verb + structured reducer failures
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-EXEC.md:340:### 2N.7 Report/reducer rail-policy alignment (via 2N.8)
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-EXEC.md:352:### 2N.8 Shared bundle read layer (`BundleReader`)
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-EXEC.md:353:# The Orchestration Process
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-EXEC.md:364:## Roles: a lead, independent implementers/reviewers, and a human at the top
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-EXEC.md:397:## The loop, end to end
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-EXEC.md:462:### Stop cards and paused work
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-EXEC.md:465:updates an `ACTIVE_STOP_CARD` at the top of `RUN_STATE.md`. While active,
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-EXEC.md:494:## The artifact system (where rigor becomes auditable)
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-EXEC.md:541:## Council discipline
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-EXEC.md:562:## Spend guardrails (WO-022; R2 ruled, Ed-ratified 2026-07-13)
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-EXEC.md:617:# JouleWise Run State
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-EXEC.md:632:## ⏳ 2026-08-07 — paper-first session (LIVE; interim block, refreshed mid-flight)
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-EXEC.md:663:## ✅ CHECKPOINT 2026-08-06 late — machine-move stop (resume script)
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-EXEC.md:717:## ⏳ 2026-08-06 AFTERNOON — re-mint fork: historical consumption is closed at main; Ed's ruling owed
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-EXEC.md:772:## ✅ CHECKPOINT 2026-08-06 morning — executed by the afternoon session above
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-EXEC.md:797:## Start Here For Every Big Run
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-EXEC.md:817:12. If an `ACTIVE_STOP_CARD` exists below, it overrides every normal
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-EXEC.md:846:## Historical Stop-Card Note
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-EXEC.md:852:## ACTIVE_STOP_CARD
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-EXEC.md:856:## Active Global Work-Selection Gates
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-EXEC.md:860:## Restart By Machine-State Lane
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-EXEC.md:864:### [ED-EXTERNAL]
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-EXEC.md:868:### [QUIET-MAC]
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-EXEC.md:872:### [AGENT]
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-EXEC.md:878:## CHECKPOINT 2026-07-18 (late): D-077 adversarial arc complete, PR #77 open
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-EXEC.md:884:## Current Project Status
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-EXEC.md:891:### The central measurement fact (read before any measurement decision)
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-EXEC.md:903:### Collection state
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-EXEC.md:937:### The critical path: build the mint (HISTORICAL — CLOSED 2026-07-30)
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-EXEC.md:972:### Disk
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-EXEC.md:996:### Orchestration
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-EXEC.md:1004:### What needs Ed
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-EXEC.md:1060:#59 integration-review fixes and the #60 DOC-008 kernel refresh); none
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-EXEC.md:1083:## Known Workspace State
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-EXEC.md:1150:## Historical Next-Work Snapshot (superseded 2026-07-15)
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-EXEC.md:1168:## Current Do-Not-Do-Yet List
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-EXEC.md:1196:## Current Queue
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-EXEC.md:1274:## Active Global Work-Selection Gates
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-EXEC.md:1278:### [ED-EXTERNAL] lane
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-EXEC.md:1289:### [QUIET-MAC] lane
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-EXEC.md:1302:### [AGENT] lane
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-EXEC.md:14348:## impl/d117-u3-pinset-v2...origin/main [behind 14]
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-EXEC.md:14671:## impl/d117-u3-pinset-v2...origin/main [behind 14]
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-EXEC.md:15054:## impl/d117-u3-pinset-v2...origin/main [behind 14]
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-EXEC.md:15108:## Findings
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-EXEC.md:15186:## Refusal-vector audit
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-EXEC.md:15201:## Commands and results
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-EXEC.md:15265:## Findings
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-EXEC.md:15343:## Refusal-vector audit
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-EXEC.md:15358:## Commands and results
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-CONTRACT.md:18:/bin/zsh -lc 'git status --short --branch && rg -n "ACTIVE_STOP_CARD|Current Project Status|Known Workspace State|What Is Next" RUN_STATE.md && rg -n "Current Queue|Do-Not-Do-Yet" TASK_QUEUE.md && rg -n "Mission M0|M0" docs/agent_playbook.md' in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u3
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-CONTRACT.md:20:## impl/d117-u3-pinset-v2...origin/main [behind 13]
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-CONTRACT.md:25:2004:12. If an `ACTIVE_STOP_CARD` exists below, it overrides every normal
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-CONTRACT.md:26:2039:## ACTIVE_STOP_CARD
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-CONTRACT.md:27:2178:## Current Project Status
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-CONTRACT.md:28:2739:## Known Workspace State
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-CONTRACT.md:37:/bin/zsh -lc "sed -n '2039,2235p' RUN_STATE.md; sed -n '2739,2825p' RUN_STATE.md; rg -n \""'^## .*What Is Next|What Is Next" RUN_STATE.md; sed -n '"'50,125p' docs/agent_playbook.md; sed -n '213,390p' TASK_QUEUE.md; sed -n '1,240p' docs/orchestration.md" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u3
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-CONTRACT.md:39:## ACTIVE_STOP_CARD
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-CONTRACT.md:43:## Active Global Work-Selection Gates
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-CONTRACT.md:47:## Restart By Machine-State Lane
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-CONTRACT.md:51:### [ED-EXTERNAL]
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-CONTRACT.md:55:### [QUIET-MAC]
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-CONTRACT.md:59:### [AGENT]
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-CONTRACT.md:65:## CHECKPOINT 2026-07-18 (late): D-077 adversarial arc complete, PR #77 open
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-CONTRACT.md:89:## CHECKPOINT 2026-07-18: Claude script bridge runs in the pet's app task
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-CONTRACT.md:115:## CHECKPOINT 2026-07-17 (late session): env-guard branch open, review pending
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-CONTRACT.md:166:## Superseded stop card (CP-5)
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-CONTRACT.md:178:## Current Project Status
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-CONTRACT.md:185:### The central measurement fact (read before any measurement decision)
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-CONTRACT.md:197:### Collection state
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-CONTRACT.md:231:### The critical path: build the mint (HISTORICAL — CLOSED 2026-07-30)
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-CONTRACT.md:236:## Known Workspace State
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-CONTRACT.md:303:## Historical Next-Work Snapshot (superseded 2026-07-15)
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-CONTRACT.md:321:## Reference Decisions And Blockers (non-selection context)
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-CONTRACT.md:323:## Mission M0: Preflight (every session)
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-CONTRACT.md:325:1. Read only the targeted `RUN_STATE.md` sections: `ACTIVE_STOP_CARD`
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-CONTRACT.md:326:   if present, "Current Project Status", "Known Workspace State", and
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-CONTRACT.md:327:   "What Is Next". If the stop card is ACTIVE, it overrides this
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-CONTRACT.md:364:## Mission M1: Slice 2N — Pre-Hardware Hardening (queue P2-007)
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-CONTRACT.md:394:### 2N.1 `RunContext` seam + raw evidence
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-CONTRACT.md:399:## Current Do-Not-Do-Yet List
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-CONTRACT.md:427:## Queue Maintenance
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-CONTRACT.md:440:## Intake Batch Owed To The Kernel (2026-07-30/31)
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-CONTRACT.md:492:## Current Queue
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-CONTRACT.md:570:## Active Global Work-Selection Gates
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-CONTRACT.md:574:### [ED-EXTERNAL] lane
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-CONTRACT.md:577:# The Orchestration Process
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-CONTRACT.md:588:## Roles: a lead, independent implementers/reviewers, and a human at the top
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-CONTRACT.md:621:## The loop, end to end
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-CONTRACT.md:686:### Stop cards and paused work
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-CONTRACT.md:689:updates an `ACTIVE_STOP_CARD` at the top of `RUN_STATE.md`. While active,
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-CONTRACT.md:718:## The artifact system (where rigor becomes auditable)
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-CONTRACT.md:765:## Council discipline
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-CONTRACT.md:786:## Spend guardrails (WO-022; R2 ruled, Ed-ratified 2026-07-13)
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-CONTRACT.md:4421:### F2 — The mint path needs a real v2, not another widened literal list (blocker)
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-CONTRACT.md:4441:### F3 — The D-102 successor packet is a pre-arm dependency (blocker)
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-CONTRACT.md:4457:### F4 — Referenced trace missing (should-fix)
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-CONTRACT.md:4468:### F5 — Queue terminology is superseded (should-fix)
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-CONTRACT.md:4472:### Ranked design decisions and rejected alternatives
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-CONTRACT.md:4488:### Proven template lineage
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-CONTRACT.md:4497:### Prefill floor claim eligibility
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-CONTRACT.md:4512:### Two-stage mint freeze
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-CONTRACT.md:4549:### Synthetic three-window live-ledger regression
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-CONTRACT.md:4609:## D-082: Floor-mint execution semantics — basis-pinned consumption and the cross-window v2 artifact
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-CONTRACT.md:4645:## D-083: The additive effective-clearable-effect expression is a disclosure obligation, not an acceptance threshold
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-CONTRACT.md:4705:## D-084: Operative decode-floor pin re-set to the composed cell gate 7.377086 J
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-CONTRACT.md:4734:## D-095: MANIFEST-CONTRAST design — analysis-manifest v3 with cross-stack armwise-max floor gating
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-CONTRACT.md:4780:## D-102: CAL-BRACKET-D079-01 pins ratified — corpus-derived budget cap, identity-epoch freshness, never-zero allowance, decimal numeric semantics
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-CONTRACT.md:4832:## D-110: Mint 1 retroactively NON-CLAIM-BEARING (taint-and-remint); RT-2 dependency edge minted; the night consult's 7B-mint license SUSPENDED
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-CONTRACT.md:4871:## D-117: D-110's historical re-mint order SUPERSEDED — prospective three-window replacement (Option 2) adopted; D-113 readiness rewired
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-CONTRACT.md:5211:   281	RUN_STATE.md:2039:## ACTIVE_STOP_CARD
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-CONTRACT.md:5221:   291	RUN_STATE.md:2178:## Current Project Status
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-CONTRACT.md:5231:   301	RUN_STATE.md:2739:## Known Workspace State
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-CONTRACT.md:5447:   517	12. If an `ACTIVE_STOP_CARD` exists below, it overrides every normal
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-CONTRACT.md:5482:   552	## ACTIVE_STOP_CARD
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-CONTRACT.md:5508:   578	## Current Project Status
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-CONTRACT.md:5641:   711	## Known Workspace State
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-CONTRACT.md:5722:   792	6. If `RUN_STATE.md` contains an ACTIVE `ACTIVE_STOP_CARD`, that card
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-CONTRACT.md:6013:  1083	1. Read only the targeted `RUN_STATE.md` sections: `ACTIVE_STOP_CARD`
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-CONTRACT.md:6014:  1084	   if present, "Current Project Status", "Known Workspace State", and
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-CONTRACT.md:6015:  1085	   "What Is Next". If the stop card is ACTIVE, it overrides this
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-CONTRACT.md:6164:  1234	updates an `ACTIVE_STOP_CARD` at the top of `RUN_STATE.md`. While active,
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-CONTRACT.md:6494:  1564	## Known Workspace State
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-CONTRACT.md:19854:## D-109 addendum II: reviewed mint-core interface amendment (integration-collision resolution); D-110 oracle clarification
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-CONTRACT.md:19892:## D-117: D-110's historical re-mint order SUPERSEDED — prospective three-window replacement (Option 2) adopted; D-113 readiness rewired
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-CONTRACT.md:20621:# Attempt a valid desk-stage document through the mint loader.
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-CONTRACT.md:21034:## impl/d117-u3-pinset-v2...origin/main [behind 14]
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-CONTRACT.md:21557:# Contract audit verdict: BLOCK
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-CONTRACT.md:21561:## Findings
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-CONTRACT.md:21613:## Requirements disposition
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-CONTRACT.md:21626:# Contract audit verdict: BLOCK
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-CONTRACT.md:21630:## Findings
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-CONTRACT.md:21682:## Requirements disposition

exec
/bin/zsh -lc "sed -n '2043,2068p' RUN_STATE.md; sed -n '2182,2380p' RUN_STATE.md; sed -n '2743,2810p' RUN_STATE.md; sed -n '213,240p' TASK_QUEUE.md; sed -n '306,462p' TASK_QUEUE.md; sed -n '50,90p' docs/agent_playbook.md; sed -n '1,260p' docs/orchestration.md" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u3
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
   it is a pre-registration change and therefore Ed's call.
5. Window B's disposition.
6. (2026-07-28 late) Multi-session coordination: a concurrent session
   force-rewrote main history (no content lost this time, but the mode
   can silently drop peer commits). Whether to adopt a
   no-force-push/branch-only convention is Ed's call.
7. (2026-07-28 late) TEST-SPEED-01's structural lever — a PR-fast/full
   CI split — is a CI-contract change and Ed's call; the
   consolidate/redesign work (~3-4 min, no deletions) needs no ruling.

Records: `docs/run_reports/2026-07-30-mint-merge-coldgate.md` (freshest
session record), `docs/process_traces/RESUME-2026-07-28.md` (superseded
as a pointer), `RESUME-2026-07-27.md`,
`RESUME-2026-07-26.md`, `docs/process_traces/2026-07-26-prereg-clock-mitigation.md`,
`docs/run_reports/2026-07-23-window-a-collection-arc.md`, and
`docs/run_reports/2026-07-24-screen-budget-gauntlet.md`.

**Historical (2026-07-25, superseded by the block above):** main
`c3e2647` contained the merged instrument repair (PR #79) and the merged
SCREEN+BUDGET rules (PR #85); the 229-member a5-a8 collection is
non-claim-bearing diagnostic, instrument-proving evidence, and the next
claim attempt was then framed as one clean prospective quiet window per
`docs/phase_2/window_runbook.md`.

The D-078 Phase-0 instrument repair was signed off and merged through
PR #79 on 2026-07-22. Registered limitation L1 remains owned by
FLOOR-BIND-01; it does not reopen the completed repair. Record:
`docs/run_reports/2026-07-20-p0-instrument-repair.md`. Earlier arcs below
are historical.

**C-028 CLOSED (2026-07-11): the full hardening + analysis-engine arc is
on main.** Reducer lattice 0.4.2 (inter-token metric) / 0.4.1 (idle ESS,
HAC variance — local r1's 47x underestimate closed) / 0.4.0 (verdict
split + window_evidence_precheck) with frozen legacy arms; the analysis
trio complete (P2-042 manifest → P2-041 verdict split → P2-037
contrast/claim engine with unwaivable cleanup claim gating per the
two-layer waiver reconciliation); doctor preflight; publication privacy
pack (fail-closed inventory); packaging CI; primary-verified related
work; load-transition prep (B remains [QUIET-MAC]). Window A's software
gates are ALL satisfied; execution needs a quiet machine + Ed.

PRs #41-#60 form the landed C-028 arc, all merged 2026-07-11 (incl. the
#59 integration-review fixes and the #60 DOC-008 kernel refresh); none
implies live evidence. P0-003 is satisfied
by the verified iCloud backup/restore. All NVIDIA/Orin protocol pins remain
PROVISIONAL pending P1-006 live evidence.

**Historical restart snapshot (recorded 2026-07-13; non-operative).** The
numbered sequence below is retained as dated handoff narrative, not current
work-selection authority. Use the generated region above for selection.
1. DONE 2026-07-13: #61-#63 merged at delta-audited heads; site deployed
   live under the cap; XSI-1 CI hardening green on main; bridge landed
   and lead-verified (8/8 protocol checks; suite 1318 OK).
2. [ED + AGENT] **Comprehensive whole-project audit (declared gate).**
   The audit method proposal is with Ed; no further feature work, queue
   pulls, or campaign prep until the audit runs and its findings are
   adjudicated. Audit focus per Ed: overproduction (excess code/tests),
   plus everything a serious external review would check.
3. [QUIET-MAC + ED] After the audit: Window A — C-019 production-shaped
   shakedown and P2-015-SMOKE, then P2-015 floors and P2-006 baselines.
   Do not run this lane while an agent session is active.
4. [AGENT] Post-audit, outside a quiet window: P2-050 adjudication,
   SITE-02 follow-ups, P2-027 publication prep. P2-022/P2-023 remain
   blocked until the 2M corpus exists.

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


exec
/bin/zsh -lc "git merge-base origin/main HEAD; git rev-list --left-right --count origin/main...HEAD; git diff --stat origin/main...HEAD; git diff --name-status origin/main...HEAD; git show --stat --oneline --decorate --no-renames HEAD; git show --format=fuller --no-ext-diff --find-renames --name-only HEAD | sed -n '1,120p'" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u3
 succeeded in 0ms:
0d9392f460b1284fd39d07ff52b2d97005b7b317
15	3
 joulewise/detection_floor.py                  |  542 ++++-
 scripts/floor_mint_pinsets/schema_v2.json     |  919 +++++++++
 scripts/mint_floor_artifact_generalized.py    | 2614 ++++++++++++++++++++++++-
 tests/test_mint_floor_artifact_generalized.py | 1785 +++++++++++++++++
 4 files changed, 5799 insertions(+), 61 deletions(-)
M	joulewise/detection_floor.py
A	scripts/floor_mint_pinsets/schema_v2.json
M	scripts/mint_floor_artifact_generalized.py
M	tests/test_mint_floor_artifact_generalized.py
454f777 (HEAD -> impl/d117-u3-pinset-v2, origin/impl/d117-u3-pinset-v2) U3 FIX-1b/6b/8: authenticated postcollection pins (named equality check per custody field against supplied evidence — presence no longer satisfies a pin), three-way six-decimal/full-precision/report consistency with the coordinated-inconsistency regression, production-CLI authentication path test, implementation-independent golden fixture
 scripts/floor_mint_pinsets/schema_v2.json     |   2 +-
 scripts/mint_floor_artifact_generalized.py    | 126 +++++--
 tests/test_mint_floor_artifact_generalized.py | 497 +++++++++++++++++++++++++-
 3 files changed, 582 insertions(+), 43 deletions(-)
commit 454f77795f5ed2f1841055a7ce125e1456f583de
Author:     Ed R <edr@Eds-MacBook-Pro.local>
AuthorDate: Fri Aug 7 13:10:51 2026 -0700
Commit:     Ed R <edr@Eds-MacBook-Pro.local>
CommitDate: Fri Aug 7 13:10:51 2026 -0700

    U3 FIX-1b/6b/8: authenticated postcollection pins (named equality check per custody field against supplied evidence — presence no longer satisfies a pin), three-way six-decimal/full-precision/report consistency with the coordinated-inconsistency regression, production-CLI authentication path test, implementation-independent golden fixture
    
    Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>

scripts/floor_mint_pinsets/schema_v2.json
scripts/mint_floor_artifact_generalized.py
tests/test_mint_floor_artifact_generalized.py

codex
Preflight is clear: no active stop card, this is an `[AGENT]` read-only review, and the worktree is clean. The branch is exactly at the requested `454f777`; `origin/main` has advanced independently, so I’m treating `HEAD^..HEAD` as the round-2 delta while using the origin/main U3 records as the prior-audit baseline.
exec
/bin/zsh -lc "sed -n '15100,15395p' docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-EXEC.md; rg -n \"FIX-1b|FIX-6b|FIX-8|presence-only|self-attest|authentication|evidence artifact|receipt|drift|allowance\" docs/process_traces/2026-08-07-d117-u-units/U3-FIX-CONTRACT.md | tail -160; git show HEAD"'^:scripts/mint_floor_artifact_generalized.py | rg -n "custody|receipt|digest|bracket|ledger|extraction|drift|allowance|evidence" | head -240' in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u3
 succeeded in 0ms:
PY" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u3
 succeeded in 691ms:
shared_validator_errors= []
generalized_validator= MintError pinset.producer_plans[0].plan schema mismatch: extra=['silently_ignored_extra']

codex
Verdict: **BLOCK / do not merge.** The focused tests pass, but mutation probes found authentication bypasses and a validator crash. No repository files were modified.

## Findings

1. **P0 — Required v2 “authentication” pins are presence-only and can lie about the evidence.**  
   [scripts/mint_floor_artifact_generalized.py:465](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u3/scripts/mint_floor_artifact_generalized.py:465), [scripts/mint_floor_artifact_generalized.py:1496](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u3/scripts/mint_floor_artifact_generalized.py:1496)

   The parser syntax-checks receipt, ledger, extraction-report, plan-sidecar, model/runtime, and calibration-acceptance hashes, but `_v2_gate_component` authenticates only extraction spec, order manifest, metric/window, and member/config pins.

   Concrete reproduced scenario: changed the pinned extraction-report SHA from the actual `111…111` to `999…999`, plus unrelated pre-receipt and runtime hashes, recomputed the aggregate producer hashes, and minted successfully:

   ```text
   MINT_SUCCEEDED
   actual_report_sha= 111111...111
   pinned_report_sha= 999999...999
   pinned_pre_receipt_sha= 888888...888
   pinned_runtime_identity_sha= 777777...777
   validator_errors= []
   ```

   Thus “missing/unresolved pin refuses” is only a structural test. A present but false resolved pin is accepted.

2. **P1 — Aggregate transport allowlists are ignored after shape validation.**  
   [scripts/mint_floor_artifact_generalized.py:830](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u3/scripts/mint_floor_artifact_generalized.py:830), [scripts/mint_floor_artifact_generalized.py:1635](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u3/scripts/mint_floor_artifact_generalized.py:1635)

   The aggregate list is checked for group/cell IDs and field shape, but its allowed families are never compared with each cell’s pins. Construction uses only the cell-level list.

   Reproduced:

   ```text
   MINT_SUCCEEDED
   aggregate_pin= aggregate-only-family aaaaa...aaaaa
   emitted_group= synthetic-0-decode b0a5...84cf
   validator_errors= []
   ```

   A contradictory authenticated aggregate declaration therefore mints and validates.

3. **P1 — The shared validator’s v2 “closed schema” projection silently accepts nested extra fields.**  
   [joulewise/detection_floor.py:1599](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u3/joulewise/detection_floor.py:1599)

   `_project_floor_mint_pinset_v2` checks producer top-level keys but does not close nested plan/cell/component objects. A plan with `silently_ignored_extra: true` produced:

   ```text
   shared_validator_errors= []
   generalized_validator= MintError ... schema mismatch: extra=['silently_ignored_extra']
   ```

   Existing callers of `joulewise.detection_floor.validate_floor_artifact`, including claim ingestion, therefore disagree with the mint validator about whether a v2 pinset is valid.

4. **P1 — Malformed v2 provenance crashes the shared validator.**  
   [joulewise/detection_floor.py:2003](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u3/joulewise/detection_floor.py:2003)

   Invalid values are added to sets even after type validation fails. Setting a producer `plan_id` to `[]` yielded:

   ```text
   CRASH TypeError unhashable type: 'list'
   ```

   This breaks the validator’s error-list contract and propagates through `authenticate_floor_artifact_bytes`.

5. **P2 — Runtime parsing disagrees with `schema_v2.json` on decimal and boolean closure.**  
   [scripts/mint_floor_artifact_generalized.py:318](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u3/scripts/mint_floor_artifact_generalized.py:318), [scripts/mint_floor_artifact_generalized.py:493](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u3/scripts/mint_floor_artifact_generalized.py:493)

   The schema requires plain unsigned decimal strings and integer `1`; runtime accepts Decimal-equivalent spellings and `True == 1`.

   Reproduced final pinset:

   ```text
   MINT_SUCCEEDED observed=-0 applied=1.0818E-2 embedding_count=true
   validator_errors= []
   ```

   Six-decimal floor literals themselves behaved correctly: negative zero, missing trailing zeros, leading zero, comma decimal, exponent, and leading plus all refused. `format(..., ".6f")` is locale-independent and preserves six trailing decimals.

6. **P2 — No positive test executes the production v2 file-authentication/CLI path.**  
   [tests/test_mint_floor_artifact_generalized.py:985](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u3/tests/test_mint_floor_artifact_generalized.py:985), [tests/test_mint_floor_artifact_generalized.py:1018](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u3/tests/test_mint_floor_artifact_generalized.py:1018)

   The successful v2 test injects already-authenticated component objects into `mint_multi_cell_authenticated_artifact`. The sole v2 CLI test checks only that omitting `--v2-input-manifest` refuses. No test invokes `_authenticate_v2_inputs` or `mint_multi_cell_floor_artifact` successfully. A regression that always rejects a supplied manifest—or authenticates the wrong files—would leave all 27 focused tests green.

## Refusal-vector audit

| Claimed vector | Assessment |
|---|---|
| Desk-stage file used for mint | Real parser mutation test; it would catch allowing the requirements schema version. |
| Missing/unresolved pin | Real for missing fields/placeholder object, but materially incomplete: false “resolved” hashes mint successfully (P0). |
| Derived-literal attempt | Real type-sensitive parser test. |
| Cross-cell sum | Covered at the consumer layer by `test_cross_stack_armwise_floor_is_max_never_sum...` and `test_combined_floor_uses_every_selected...`. The new test’s “sum” case is only same-cell absolute+comparative. |
| Allowance omitted/doubled | Real for the declarative count field, but `True` bypasses it and several allowance/provenance pins are not bound to evidence. |
| Wrong metric/phase-precheck | Real parser tests; component metric/window are also checked at the construction gate. |
| `7.377086` reuse | Real exact-literal refusal test. |
| Aggregate/component hash mismatch | Real end-to-end mutations, but it does not cover contradictory aggregate allowlists or false evidence hashes. |

The synthetic hash-freezing helper derives expected component hashes using the implementation under test, so the happy-path test is not an independent golden oracle.

## Commands and results

```text
PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/joulewise-audit-pycache \
python3 -m unittest -v tests.test_mint_floor_artifact_generalized
```

```text
Ran 27 tests in 1.912s
OK
```

```text
PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/joulewise-audit-pycache \
python3 -m unittest -v tests.test_mint_floor_artifact
```

```text
Ran 34 tests in 0.598s
OK
```

Shared-caller regression set:

```text
python3 -m unittest -v \
  tests.test_detection_floor \
  tests.test_analysis_claims \
  tests.test_analysis_integration
```

```text
Ran 249 tests in 27.061s
OK
```

Required full suite, unpiped:

```text
PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/joulewise-audit-pycache \
python3 -m unittest discover -s tests
```

Exact unittest tail:

```text
Ran 2677 tests in 755.120s

FAILED (failures=1, skipped=87)
```

The sole failure was exactly the permitted stale-branch D-117 docs-index mismatch:

```text
FAIL: test_decision_index_matches_decision_bodies
First extra element 116:
'D-117'
```

No other suite failure occurred. `git diff --check` exited 0. Final `git status` retained exactly the original four dirty paths; no repository files were changed.
tokens used
236,881
Verdict: **BLOCK / do not merge.** The focused tests pass, but mutation probes found authentication bypasses and a validator crash. No repository files were modified.

## Findings

1. **P0 — Required v2 “authentication” pins are presence-only and can lie about the evidence.**  
   [scripts/mint_floor_artifact_generalized.py:465](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u3/scripts/mint_floor_artifact_generalized.py:465), [scripts/mint_floor_artifact_generalized.py:1496](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u3/scripts/mint_floor_artifact_generalized.py:1496)

   The parser syntax-checks receipt, ledger, extraction-report, plan-sidecar, model/runtime, and calibration-acceptance hashes, but `_v2_gate_component` authenticates only extraction spec, order manifest, metric/window, and member/config pins.

   Concrete reproduced scenario: changed the pinned extraction-report SHA from the actual `111…111` to `999…999`, plus unrelated pre-receipt and runtime hashes, recomputed the aggregate producer hashes, and minted successfully:

   ```text
   MINT_SUCCEEDED
   actual_report_sha= 111111...111
   pinned_report_sha= 999999...999
   pinned_pre_receipt_sha= 888888...888
   pinned_runtime_identity_sha= 777777...777
   validator_errors= []
   ```

   Thus “missing/unresolved pin refuses” is only a structural test. A present but false resolved pin is accepted.

2. **P1 — Aggregate transport allowlists are ignored after shape validation.**  
   [scripts/mint_floor_artifact_generalized.py:830](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u3/scripts/mint_floor_artifact_generalized.py:830), [scripts/mint_floor_artifact_generalized.py:1635](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u3/scripts/mint_floor_artifact_generalized.py:1635)

   The aggregate list is checked for group/cell IDs and field shape, but its allowed families are never compared with each cell’s pins. Construction uses only the cell-level list.

   Reproduced:

   ```text
   MINT_SUCCEEDED
   aggregate_pin= aggregate-only-family aaaaa...aaaaa
   emitted_group= synthetic-0-decode b0a5...84cf
   validator_errors= []
   ```

   A contradictory authenticated aggregate declaration therefore mints and validates.

3. **P1 — The shared validator’s v2 “closed schema” projection silently accepts nested extra fields.**  
   [joulewise/detection_floor.py:1599](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u3/joulewise/detection_floor.py:1599)

   `_project_floor_mint_pinset_v2` checks producer top-level keys but does not close nested plan/cell/component objects. A plan with `silently_ignored_extra: true` produced:

   ```text
   shared_validator_errors= []
   generalized_validator= MintError ... schema mismatch: extra=['silently_ignored_extra']
   ```

   Existing callers of `joulewise.detection_floor.validate_floor_artifact`, including claim ingestion, therefore disagree with the mint validator about whether a v2 pinset is valid.

4. **P1 — Malformed v2 provenance crashes the shared validator.**  
   [joulewise/detection_floor.py:2003](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u3/joulewise/detection_floor.py:2003)

   Invalid values are added to sets even after type validation fails. Setting a producer `plan_id` to `[]` yielded:

   ```text
   CRASH TypeError unhashable type: 'list'
   ```

   This breaks the validator’s error-list contract and propagates through `authenticate_floor_artifact_bytes`.

5. **P2 — Runtime parsing disagrees with `schema_v2.json` on decimal and boolean closure.**  
   [scripts/mint_floor_artifact_generalized.py:318](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u3/scripts/mint_floor_artifact_generalized.py:318), [scripts/mint_floor_artifact_generalized.py:493](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u3/scripts/mint_floor_artifact_generalized.py:493)

   The schema requires plain unsigned decimal strings and integer `1`; runtime accepts Decimal-equivalent spellings and `True == 1`.

   Reproduced final pinset:

   ```text
   MINT_SUCCEEDED observed=-0 applied=1.0818E-2 embedding_count=true
   validator_errors= []
   ```

   Six-decimal floor literals themselves behaved correctly: negative zero, missing trailing zeros, leading zero, comma decimal, exponent, and leading plus all refused. `format(..., ".6f")` is locale-independent and preserves six trailing decimals.

6. **P2 — No positive test executes the production v2 file-authentication/CLI path.**  
   [tests/test_mint_floor_artifact_generalized.py:985](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u3/tests/test_mint_floor_artifact_generalized.py:985), [tests/test_mint_floor_artifact_generalized.py:1018](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u3/tests/test_mint_floor_artifact_generalized.py:1018)

   The successful v2 test injects already-authenticated component objects into `mint_multi_cell_authenticated_artifact`. The sole v2 CLI test checks only that omitting `--v2-input-manifest` refuses. No test invokes `_authenticate_v2_inputs` or `mint_multi_cell_floor_artifact` successfully. A regression that always rejects a supplied manifest—or authenticates the wrong files—would leave all 27 focused tests green.

## Refusal-vector audit

| Claimed vector | Assessment |
|---|---|
| Desk-stage file used for mint | Real parser mutation test; it would catch allowing the requirements schema version. |
| Missing/unresolved pin | Real for missing fields/placeholder object, but materially incomplete: false “resolved” hashes mint successfully (P0). |
| Derived-literal attempt | Real type-sensitive parser test. |
| Cross-cell sum | Covered at the consumer layer by `test_cross_stack_armwise_floor_is_max_never_sum...` and `test_combined_floor_uses_every_selected...`. The new test’s “sum” case is only same-cell absolute+comparative. |
| Allowance omitted/doubled | Real for the declarative count field, but `True` bypasses it and several allowance/provenance pins are not bound to evidence. |
| Wrong metric/phase-precheck | Real parser tests; component metric/window are also checked at the construction gate. |
| `7.377086` reuse | Real exact-literal refusal test. |
| Aggregate/component hash mismatch | Real end-to-end mutations, but it does not cover contradictory aggregate allowlists or false evidence hashes. |

The synthetic hash-freezing helper derives expected component hashes using the implementation under test, so the happy-path test is not an independent golden oracle.

## Commands and results

```text
PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/joulewise-audit-pycache \
python3 -m unittest -v tests.test_mint_floor_artifact_generalized
```

```text
Ran 27 tests in 1.912s
OK
```

```text
PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/joulewise-audit-pycache \
python3 -m unittest -v tests.test_mint_floor_artifact
```

```text
Ran 34 tests in 0.598s
OK
```

Shared-caller regression set:

```text
python3 -m unittest -v \
  tests.test_detection_floor \
  tests.test_analysis_claims \
  tests.test_analysis_integration
```

```text
Ran 249 tests in 27.061s
OK
```

Required full suite, unpiped:

11:become AUTHENTICATED, not self-attested. The mint must take the actual evidence
13:COMPARE every pinned receipt id/content digest, binding hash, terminal head,
14:extraction-report hash, observed_drift_s, and applied_allowance_s against them;
16:fabrication scenario (all hashes replaced + drift/allowance tampered + self-hashes
48:FIX-7 (exec lens): (a) the allowance-count declarative field must not be bypassable
2:"""Mint a floor artifact with a digest-authenticated per-plan pinset.
46:V2_ALLOWANCE_RULE = "max(observed_drift_s,0.010818)"
51:    "joulewise.floor_mint_extraction_postcollection.v2"
53:V2_BRACKET_BINDING_SCHEMA = "joulewise.calibration_bracket_binding.v1"
99:        "(evidence_root_id: 'str', evidence_root: 'Path', report_path: 'Path', "
127:        "calibration_ledger_snapshot: 'CalibrationLedgerSnapshot | None' = None) "
131:# D-109 R1.4 added the immutable ledger-snapshot parameter. Any future
132:# change requires explicit signature-pin review plus parity evidence.
167:    evidence_root_id: str
171:    extraction_spec_members: int
173:    drift_allowance_j: float
203:    evidence_root: Path
220:    evidence_root: Path
226:    bracket_binding: Mapping[str, Any]
227:    bracket_binding_sha256: str
256:def _evidence_root_id(value: object, label: str) -> str:
293:            "evidence_root_id",
297:            "extraction_spec_members",
299:            "drift_allowance_j",
304:        evidence_root_id=_evidence_root_id(
305:            row["evidence_root_id"], f"{label}.evidence_root_id"
318:        extraction_spec_members=_positive_int(
319:            row["extraction_spec_members"],
320:            f"{label}.extraction_spec_members",
323:        drift_allowance_j=_nonnegative_number(
324:            row["drift_allowance_j"], f"{label}.drift_allowance_j"
368:    bundle_ids = [bundle_id for bundle_id, _digest in result]
407:            "evidence_root_id",
411:            "extraction_spec_sha256",
412:            "extraction_spec_members",
414:            "drift_allowance_j",
422:    extraction_count = _positive_int(
423:        row["extraction_spec_members"], f"{label}.extraction_spec_members"
427:    # against the supplied component evidence before construction.
428:    _sha256(row["extraction_spec_sha256"], f"{label}.extraction_spec_sha256")
431:        evidence_root_id=_evidence_root_id(
432:            row["evidence_root_id"], f"{label}.evidence_root_id"
445:        extraction_spec_members=extraction_count,
447:        drift_allowance_j=_nonnegative_number(
448:            row["drift_allowance_j"], f"{label}.drift_allowance_j"
476:            "pre_receipt_sha256",
478:            "post_receipt_sha256",
480:            "bracket_binding_sha256",
481:            "terminal_ledger_head_sha256",
482:            "observed_drift_s",
483:            "allowance_rule",
484:            "bracket_screen_s",
485:            "applied_allowance_s",
486:            "allowance_embedding_count",
487:            "extraction_report_sha256",
499:        "pre_receipt_sha256",
501:        "post_receipt_sha256",
503:        "bracket_binding_sha256",
504:        "terminal_ledger_head_sha256",
505:        "extraction_report_sha256",
516:    if row["allowance_rule"] != V2_ALLOWANCE_RULE:
518:            f"{label}.allowance_rule must equal {V2_ALLOWANCE_RULE!r}"
520:    if row["bracket_screen_s"] != V2_BRACKET_SCREEN_S:
522:            f"{label}.bracket_screen_s must equal {V2_BRACKET_SCREEN_S!r}"
525:        isinstance(row["allowance_embedding_count"], bool)
526:        or not isinstance(row["allowance_embedding_count"], int)
527:        or row["allowance_embedding_count"] != 1
530:            f"{label}.allowance_embedding_count must equal 1 (once per cell)"
532:    observed = _decimal_text(row["observed_drift_s"], f"{label}.observed_drift_s")
534:        row["applied_allowance_s"], f"{label}.applied_allowance_s"
538:            f"{label}.applied_allowance_s does not apply the never-zero rule once"
593:                "evidence_root_id",
596:                "extraction_spec",
631:        evidence_root_id = _evidence_root_id(
632:            producer["evidence_root_id"], f"{label}.evidence_root_id"
658:        extraction = _object(
659:            producer["extraction_spec"],
660:            f"{label}.extraction_spec",
663:        _sha256(extraction["sha256"], f"{label}.extraction_spec.sha256")
665:            extraction["member_count"],
666:            f"{label}.extraction_spec.member_count",
700:        producer_custody_pins: list[tuple[object, ...]] = []
763:            if absolute.evidence_root_id != evidence_root_id or (
764:                comparative.evidence_root_id != evidence_root_id
767:                    f"{cell_label}: component evidence_root_id must equal the producer root"
772:                    component["extraction_spec_sha256"] != extraction["sha256"]
773:                    or component["extraction_spec_members"]
774:                    != extraction["member_count"]
777:                        f"{cell_label}.{component_name}: extraction-spec inventory "
784:            producer_custody_pins.append(
788:                        "pre_receipt_sha256",
790:                        "post_receipt_sha256",
792:                        "bracket_binding_sha256",
793:                        "terminal_ledger_head_sha256",
794:                        "observed_drift_s",
795:                        "applied_allowance_s",
796:                        "extraction_report_sha256",
814:                bundle_id for bundle_id, _digest in _member_pins(
819:                bundle_id for bundle_id, _digest in _member_pins(
826:        if len(set(producer_custody_pins)) != 1:
828:                f"{label}.cells must share one authenticated producer custody record"
830:        if len(component_member_universe) != extraction["member_count"]:
832:                f"{label}.extraction_spec.member_count must equal the unique pinned member count"
1105:    actual = hashlib.sha256(raw).hexdigest()
1140:            "review-pinned mint-core interface drift: missing or renamed "
1147:            "review-pinned mint-core interface drift: MintError is not a "
1155:                "review-pinned mint-core interface drift: cannot inspect "
1160:                "review-pinned mint-core interface drift: "
1168:    for name in ("consumption_semantics_id", "calibration_ledger_snapshot"):
1171:                "review-pinned mint-core interface drift: mint_floor_artifact "
1239:        "A10_SPEC_MEMBERS": pinset.absolute.extraction_spec_members,
1240:        "WINDOW_C_SPEC_MEMBERS": pinset.comparative.extraction_spec_members,
1243:        "A10_DRIFT_ALLOWANCE_J": pinset.absolute.drift_allowance_j,
1244:        "WINDOW_C_DRIFT_ALLOWANCE_J": pinset.comparative.drift_allowance_j,
1287:        if absolute.evidence_root_id != pinset.absolute.evidence_root_id:
1289:                "pre-registration gate: absolute evidence-root id mismatch"
1291:        if comparative.evidence_root_id != pinset.comparative.evidence_root_id:
1293:                "pre-registration gate: comparative evidence-root id mismatch"
1318:                evidence_root_id=root_id,
1374:    """Gate and build from already-authenticated component fixtures/evidence."""
1459:                evidence_root_id=pinset.absolute.evidence_root_id,
1460:                evidence_root=absolute_inputs.evidence_root,
1468:                evidence_root_id=pinset.comparative.evidence_root_id,
1469:                evidence_root=comparative_inputs.evidence_root,
1496:    return hashlib.sha256(payload).hexdigest()
1506:    return hashlib.sha256(_artifact_payload(artifact)).hexdigest()
1580:    if actual.evidence_root_id != pins["evidence_root_id"]:
1581:        raise MintError(f"{label}: evidence root id mismatch")
1584:    if actual.spec_sha256 != pins["extraction_spec_sha256"]:
1585:        raise MintError(f"{label}: extraction spec sha256 mismatch")
1599:        "extraction_spec_members"
1601:        raise MintError(f"{label}: extraction spec member count mismatch")
1611:    if actual.whole_window_drift_allowance.get("allowance_j") != pins[
1612:        "drift_allowance_j"
1614:        raise MintError(f"{label}: energy drift allowance mismatch")
1666:def _v2_extraction_postcollection_record(
1678:            f"postcollection_evidence_mismatch: {label} extraction report "
1683:            f"postcollection_evidence_mismatch: {label} extraction report "
1694:            f"postcollection_evidence_mismatch: {label} extraction report "
1702:            "observed_drift_s",
1703:            "applied_allowance_s",
1713:    _decimal_text(row["observed_drift_s"], f"{label}.observed_drift_s")
1714:    _decimal_text(row["applied_allowance_s"], f"{label}.applied_allowance_s")
1730:def _v2_authenticate_bracket_binding(
1734:    ledger_snapshot: Any,
1737:    binding = inputs.bracket_binding
1740:        "ledger_schema",
1745:        "evidence_root_id",
1747:        "capability_receipt_digest",
1750:        "binding_digest",
1753:            f"postcollection_evidence_mismatch: {label} bracket binding schema mismatch"
1757:            f"postcollection_evidence_mismatch: {label} bracket binding version mismatch"
1759:    if binding.get("ledger_schema") != "joulewise.calibration_observation_ledger.v1":
1761:            f"postcollection_evidence_mismatch: {label} bracket ledger schema mismatch"
1763:    observed_binding_digest = _canonical_json_sha256(
1764:        {key: value for key, value in binding.items() if key != "binding_digest"}
1766:    if binding.get("binding_digest") != observed_binding_digest:
1768:            f"postcollection_evidence_mismatch: {label} binding digest mismatch"
1773:        ("evidence_root_id", producer["evidence_root_id"]),
1774:        ("runs_root", str(inputs.evidence_root.resolve(strict=False))),
1778:            f"postcollection_evidence_mismatch: {label} binding {field} mismatch"
1783:                f"postcollection_evidence_mismatch: {label} binding {field} mismatch"
1786:        binding.get("capability_receipt_digest"),
1787:        f"{label}.capability_receipt_digest",
1790:        inputs.bracket_binding_sha256,
1791:        f"{label}.bracket_binding_sha256",
1793:    if not bool(_mapping_attribute(ledger_snapshot, "valid")):
1795:            f"postcollection_evidence_mismatch: {label} ledger snapshot is invalid"
1797:    if _mapping_attribute(ledger_snapshot, "ledger_schema") != binding[
1798:        "ledger_schema"
1801:            f"postcollection_evidence_mismatch: {label} ledger snapshot schema mismatch"
1803:    receipts = _mapping_attribute(ledger_snapshot, "receipts")
1804:    observations = _mapping_attribute(ledger_snapshot, "observations")
1805:    sessions = _mapping_attribute(ledger_snapshot, "bracket_session_by_id")
1806:    if not isinstance(receipts, tuple | list) or not isinstance(
1810:            f"postcollection_evidence_mismatch: {label} ledger snapshot is incomplete"
1819:            f"postcollection_evidence_mismatch: {label} bracket session is absent"
1826:        ("evidence_root_id", binding["evidence_root_id"]),
1829:            "capability_receipt_digest",
1830:            binding["capability_receipt_digest"],
1835:                f"postcollection_evidence_mismatch: {label} bracket session {field} mismatch"
1843:            f"postcollection_evidence_mismatch: {label} finalized bracket slots mismatch"
1845:    receipt_digests = {
1846:        row.get("receipt_digest")
1847:        for row in receipts
1848:        if isinstance(row, Mapping) and _SHA256_RE.fullmatch(str(row.get("receipt_digest")))
1850:    if binding.get("capability_receipt_digest") not in receipt_digests:
1852:            f"postcollection_evidence_mismatch: {label} capability receipt is absent"
1857:            f"postcollection_evidence_mismatch: {label} binding endpoints mismatch"
1864:            "receipt_digest",
1865:            "content_digest",
1868:                f"postcollection_evidence_mismatch: {label} {role} endpoint schema mismatch"
1870:        _sha256(endpoint.get("receipt_digest"), f"{label}.{role}.receipt_digest")
1871:        _sha256(endpoint.get("content_digest"), f"{label}.{role}.content_digest")
1877:            and _mapping_attribute(observation, "receipt_digest")
1878:            == endpoint.get("receipt_digest")
1880:            == endpoint.get("content_digest")
1884:                f"postcollection_evidence_mismatch: {label} {role} receipt/content mismatch"
1894:                "receipt_digest",
1899:                f"postcollection_evidence_mismatch: {label} {role} finalized slot mismatch"
1903:            ("bracket_session_id", binding.get("session_id")),
1904:            ("bracket_slot", role),
1905:            ("bracket_window_id", binding.get("window_id")),
1906:            ("bracket_plan_id", producer["plan"]["plan_id"]),
1907:            ("bracket_plan_sha256", producer["plan"]["sha256"]),
1908:            ("bracket_evidence_root_id", producer["evidence_root_id"]),
1912:                    f"postcollection_evidence_mismatch: {label} {role} {field} mismatch"
1917:    post_receipt = _mapping_attribute(resolved[1], "receipt_digest")
1920:        or set(terminal) != {"sequence", "head_digest", "ledger_schema"}
1921:        or terminal.get("ledger_schema")
1922:        != "joulewise.calibration_observation_ledger.v1"
1925:        or terminal.get("head_digest") != post_receipt
1928:        or post_sequence > len(receipts)
1929:        or not isinstance(receipts[post_sequence - 1], Mapping)
1930:        or receipts[post_sequence - 1].get("receipt_digest") != post_receipt
1933:            f"postcollection_evidence_mismatch: {label} terminal ledger head mismatch"
1967:            f"producer {plan_id!r}: calibration acceptance evidence mismatch"
1976:    extraction_sha256s = {component.spec_sha256 for component in components}
1977:    if extraction_sha256s != {producer["extraction_spec"]["sha256"]}:
1978:        raise MintError(f"producer {plan_id!r}: extraction spec inventory mismatch")
1982:    if len(unique_members) != producer["extraction_spec"]["member_count"]:
1983:        raise MintError(f"producer {plan_id!r}: extraction member inventory mismatch")
2012:    ledger_snapshot: Any,
2015:    pre, post_observation = _v2_authenticate_bracket_binding(
2018:        ledger_snapshot=ledger_snapshot,
2020:    expected_binding_sha256 = post["bracket_binding_sha256"]
2021:    if producer_inputs.bracket_binding_sha256 != expected_binding_sha256:
2023:            "postcollection_evidence_mismatch: bracket-binding artifact sha256 mismatch"
2025:    binding = producer_inputs.bracket_binding
2027:        "pre": (post["pre_receipt_sha256"], post["pre_content_sha256"]),
2028:        "post": (post["post_receipt_sha256"], post["post_content_sha256"]),
2032:            _mapping_attribute(observation, "receipt_digest"),
2036:                f"postcollection_evidence_mismatch: {role} receipt/content pin mismatch"
2038:    if post["terminal_ledger_head_sha256"] != binding["terminal_head"][
2039:        "head_digest"
2042:            "postcollection_evidence_mismatch: terminal ledger head pin mismatch"
2045:        observed_drift = abs(
2048:                "ledger pre exact_bound_lexeme_s",
2052:                "ledger post exact_bound_lexeme_s",
2057:            "postcollection_evidence_mismatch: ledger endpoint drift is not exact Decimal evidence"
2059:    if observed_drift != _decimal_text(
2060:        post["observed_drift_s"], "postcollection.observed_drift_s"
2063:            "postcollection_evidence_mismatch: observed drift pin mismatch"
2067:        post["extraction_report_sha256"]
2070:            "postcollection_evidence_mismatch: extraction-report sha256 mismatch"

exec
/bin/zsh -lc "nl -ba scripts/mint_floor_artifact_generalized.py | sed -n '430,570p'; nl -ba scripts/mint_floor_artifact_generalized.py | sed -n '1640,2110p'; nl -ba scripts/mint_floor_artifact_generalized.py | sed -n '2110,2255p'; nl -ba scripts/mint_floor_artifact_generalized.py | sed -n '2520,2700p'; rg -n '"'^class |''^    def test_|production|CLI|golden|coordinated|evidence|custody|self'"' tests/test_mint_floor_artifact_generalized.py | tail -220" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u3
 succeeded in 0ms:
   430	        {
   431	            "evidence_root_id",
   432	            "calibration_cell_id",
   433	            "evaluation_basis_sha256",
   434	            "evaluation_basis_members",
   435	            "extraction_spec_sha256",
   436	            "extraction_spec_members",
   437	            "expected_n",
   438	            "drift_allowance_j",
   439	            "order_manifest_id",
   440	            "order_manifest_sha256",
   441	            "consumption_semantics_id",
   442	            "members",
   443	        },
   444	    )
   445	    members = _member_pins(row["members"], f"{label}.members")
   446	    extraction_count = _positive_int(
   447	        row["extraction_spec_members"], f"{label}.extraction_spec_members"
   448	    )
   449	    # Parse the additional hashes even though the v1-compatible core consumes
   450	    # only the ComponentPins projection.  The v2 gate authenticates them
   451	    # against the supplied component evidence before construction.
   452	    _sha256(row["extraction_spec_sha256"], f"{label}.extraction_spec_sha256")
   453	    _sha256(row["order_manifest_sha256"], f"{label}.order_manifest_sha256")
   454	    return ComponentPins(
   455	        evidence_root_id=_evidence_root_id(
   456	            row["evidence_root_id"], f"{label}.evidence_root_id"
   457	        ),
   458	        calibration_cell_id=_string(
   459	            row["calibration_cell_id"], f"{label}.calibration_cell_id"
   460	        ),
   461	        evaluation_basis_sha256=_sha256(
   462	            row["evaluation_basis_sha256"],
   463	            f"{label}.evaluation_basis_sha256",
   464	        ),
   465	        evaluation_basis_members=_positive_int(
   466	            row["evaluation_basis_members"],
   467	            f"{label}.evaluation_basis_members",
   468	        ),
   469	        extraction_spec_members=extraction_count,
   470	        expected_n=_positive_int(row["expected_n"], f"{label}.expected_n"),
   471	        drift_allowance_j=_nonnegative_number(
   472	            row["drift_allowance_j"], f"{label}.drift_allowance_j"
   473	        ),
   474	        order_manifest_id=_string(
   475	            row["order_manifest_id"], f"{label}.order_manifest_id"
   476	        ),
   477	        consumption_semantics_id=_semantics_id(
   478	            row["consumption_semantics_id"],
   479	            f"{label}.consumption_semantics_id",
   480	        ),
   481	    )
   482	
   483	
   484	def _semantics_id(value: object, label: str) -> str:
   485	    text = _string(value, label)
   486	    if text not in _SEMANTICS_IDS:
   487	        raise MintError(f"{label} must be a registered consumption semantics id")
   488	    return text
   489	
   490	
   491	def _parse_v2_postcollection(value: object, label: str) -> None:
   492	    row = _object(
   493	        value,
   494	        label,
   495	        {
   496	            "absolute_evaluation_basis_sha256",
   497	            "absolute_evaluation_basis_members",
   498	            "comparative_evaluation_basis_sha256",
   499	            "comparative_evaluation_basis_members",
   500	            "pre_receipt_sha256",
   501	            "pre_content_sha256",
   502	            "post_receipt_sha256",
   503	            "post_content_sha256",
   504	            "bracket_binding_sha256",
   505	            "terminal_ledger_head_sha256",
   506	            "observed_drift_s",
   507	            "allowance_rule",
   508	            "bracket_screen_s",
   509	            "applied_allowance_s",
   510	            "allowance_embedding_count",
   511	            "extraction_report_sha256",
   512	            "absolute_floor_full_precision",
   513	            "comparative_floor_full_precision",
   514	            "operative_floor_full_precision",
   515	            "absolute_floor_six_decimal",
   516	            "comparative_floor_six_decimal",
   517	            "operative_floor_six_decimal",
   518	        },
   519	    )
   520	    for name in (
   521	        "absolute_evaluation_basis_sha256",
   522	        "comparative_evaluation_basis_sha256",
   523	        "pre_receipt_sha256",
   524	        "pre_content_sha256",
   525	        "post_receipt_sha256",
   526	        "post_content_sha256",
   527	        "bracket_binding_sha256",
   528	        "terminal_ledger_head_sha256",
   529	        "extraction_report_sha256",
   530	    ):
   531	        _sha256(row[name], f"{label}.{name}")
   532	    _positive_int(
   533	        row["absolute_evaluation_basis_members"],
   534	        f"{label}.absolute_evaluation_basis_members",
   535	    )
   536	    _positive_int(
   537	        row["comparative_evaluation_basis_members"],
   538	        f"{label}.comparative_evaluation_basis_members",
   539	    )
   540	    if row["allowance_rule"] != V2_ALLOWANCE_RULE:
   541	        raise MintError(
   542	            f"{label}.allowance_rule must equal {V2_ALLOWANCE_RULE!r}"
   543	        )
   544	    if row["bracket_screen_s"] != V2_BRACKET_SCREEN_S:
   545	        raise MintError(
   546	            f"{label}.bracket_screen_s must equal {V2_BRACKET_SCREEN_S!r}"
   547	        )
   548	    if (
   549	        isinstance(row["allowance_embedding_count"], bool)
   550	        or not isinstance(row["allowance_embedding_count"], int)
   551	        or row["allowance_embedding_count"] != 1
   552	    ):
   553	        raise MintError(
   554	            f"{label}.allowance_embedding_count must equal 1 (once per cell)"
   555	        )
   556	    observed = _decimal_text(row["observed_drift_s"], f"{label}.observed_drift_s")
   557	    applied = _decimal_text(
   558	        row["applied_allowance_s"], f"{label}.applied_allowance_s"
   559	    )
   560	    if applied != max(observed, Decimal(V2_BRACKET_SCREEN_S)):
   561	        raise MintError(
   562	            f"{label}.applied_allowance_s does not apply the never-zero rule once"
   563	        )
   564	    absolute_full = _decimal_text(
   565	        row["absolute_floor_full_precision"],
   566	        f"{label}.absolute_floor_full_precision",
   567	    )
   568	    comparative_full = _decimal_text(
   569	        row["comparative_floor_full_precision"],
   570	        f"{label}.comparative_floor_full_precision",
  1640	        raise MintError(f"{label}: expected n mismatch")
  1641	    if actual.whole_window_drift_allowance.get("allowance_j") != pins[
  1642	        "drift_allowance_j"
  1643	    ]:
  1644	        raise MintError(f"{label}: energy drift allowance mismatch")
  1645	    if actual.order_manifest.get("manifest_id") != pins["order_manifest_id"]:
  1646	        raise MintError(f"{label}: order manifest id mismatch")
  1647	    if actual.consumption_semantics_id != pins["consumption_semantics_id"]:
  1648	        raise MintError(f"{label}: consumption semantics mismatch")
  1649	    observed_members = tuple(
  1650	        (member.bundle_id, member.config_sha256) for member in actual.members
  1651	    )
  1652	    expected_members = _member_pins(pins["members"], f"{label}.members")
  1653	    if observed_members != expected_members:
  1654	        raise MintError(f"{label}: exact member/config pins mismatch")
  1655	
  1656	
  1657	def _v2_spec_member_ids(spec: Mapping[str, Any]) -> tuple[str, ...]:
  1658	    """Return physical member ids across a potentially multi-metric spec."""
  1659	
  1660	    ids: list[str] = []
  1661	    cells = spec.get("cells")
  1662	    if not isinstance(cells, list):
  1663	        return ()
  1664	    for cell in cells:
  1665	        if not isinstance(cell, Mapping):
  1666	            continue
  1667	        members = cell.get("members")
  1668	        if isinstance(members, list):
  1669	            ids.extend(
  1670	                row["bundle_id"]
  1671	                for row in members
  1672	                if isinstance(row, Mapping)
  1673	                and isinstance(row.get("bundle_id"), str)
  1674	            )
  1675	        blocks = cell.get("blocks")
  1676	        if isinstance(blocks, list):
  1677	            for block in blocks:
  1678	                block_members = (
  1679	                    block.get("members") if isinstance(block, Mapping) else None
  1680	                )
  1681	                if isinstance(block_members, Mapping):
  1682	                    ids.extend(
  1683	                        member
  1684	                        for member in block_members.values()
  1685	                        if isinstance(member, str)
  1686	                    )
  1687	    return tuple(ids)
  1688	
  1689	
  1690	def _mapping_attribute(value: object, name: str) -> object:
  1691	    if isinstance(value, Mapping):
  1692	        return value.get(name)
  1693	    return getattr(value, name, None)
  1694	
  1695	
  1696	def _require_postcollection_evidence_equal(
  1697	    field: str,
  1698	    pinned: object,
  1699	    evidenced: object,
  1700	    *,
  1701	    source: str,
  1702	) -> None:
  1703	    if pinned != evidenced:
  1704	        raise MintError(
  1705	            f"postcollection_evidence_mismatch: {field} mismatch against {source}"
  1706	        )
  1707	
  1708	
  1709	def _v2_extraction_postcollection_record(
  1710	    component: Any,
  1711	    cell_id: str,
  1712	    *,
  1713	    label: str,
  1714	) -> Mapping[str, Any]:
  1715	    block = component.report.get("floor_mint_postcollection")
  1716	    if not isinstance(block, Mapping) or set(block) != {
  1717	        "schema_version",
  1718	        "cells",
  1719	    }:
  1720	        raise MintError(
  1721	            f"postcollection_evidence_mismatch: {label} extraction report "
  1722	            "has no closed floor_mint_postcollection record"
  1723	        )
  1724	    if block.get("schema_version") != V2_EXTRACTION_POSTCOLLECTION_SCHEMA:
  1725	        raise MintError(
  1726	            f"postcollection_evidence_mismatch: {label} extraction report "
  1727	            "postcollection schema mismatch"
  1728	        )
  1729	    cells = block.get("cells")
  1730	    matches = (
  1731	        [row for row in cells if isinstance(row, Mapping) and row.get("cell_id") == cell_id]
  1732	        if isinstance(cells, list)
  1733	        else []
  1734	    )
  1735	    if len(matches) != 1:
  1736	        raise MintError(
  1737	            f"postcollection_evidence_mismatch: {label} extraction report "
  1738	            f"must contain exactly one {cell_id!r} record"
  1739	        )
  1740	    row = _object(
  1741	        matches[0],
  1742	        f"{label}.floor_mint_postcollection[{cell_id}]",
  1743	        {
  1744	            "cell_id",
  1745	            "observed_drift_s",
  1746	            "applied_allowance_s",
  1747	            "absolute_floor_full_precision",
  1748	            "comparative_floor_full_precision",
  1749	            "operative_floor_full_precision",
  1750	            "absolute_floor_six_decimal",
  1751	            "comparative_floor_six_decimal",
  1752	            "operative_floor_six_decimal",
  1753	        },
  1754	    )
  1755	    _string(row["cell_id"], f"{label}.cell_id")
  1756	    _decimal_text(row["observed_drift_s"], f"{label}.observed_drift_s")
  1757	    _decimal_text(row["applied_allowance_s"], f"{label}.applied_allowance_s")
  1758	    for name in (
  1759	        "absolute_floor_full_precision",
  1760	        "comparative_floor_full_precision",
  1761	        "operative_floor_full_precision",
  1762	    ):
  1763	        _decimal_text(row[name], f"{label}.{name}")
  1764	    for name in (
  1765	        "absolute_floor_six_decimal",
  1766	        "comparative_floor_six_decimal",
  1767	        "operative_floor_six_decimal",
  1768	    ):
  1769	        _six_decimal(row[name], f"{label}.{name}")
  1770	    for component_name in ("absolute", "comparative", "operative"):
  1771	        _verify_six_decimal_rendering(
  1772	            row[f"{component_name}_floor_full_precision"],
  1773	            row[f"{component_name}_floor_six_decimal"],
  1774	            label=f"{label}.{component_name}_floor",
  1775	        )
  1776	    return row
  1777	
  1778	
  1779	def _v2_authenticate_bracket_binding(
  1780	    *,
  1781	    producer: Mapping[str, Any],
  1782	    inputs: V2ProducerInputs,
  1783	    ledger_snapshot: Any,
  1784	) -> tuple[Any, Any]:
  1785	    label = f"producer {producer['plan']['plan_id']!r}"
  1786	    binding = inputs.bracket_binding
  1787	    if not isinstance(binding, Mapping) or set(binding) != {
  1788	        "schema_version",
  1789	        "ledger_schema",
  1790	        "session_id",
  1791	        "window_id",
  1792	        "plan_id",
  1793	        "plan_sha256",
  1794	        "evidence_root_id",
  1795	        "runs_root",
  1796	        "capability_receipt_digest",
  1797	        "terminal_head",
  1798	        "endpoints",
  1799	        "binding_digest",
  1800	    }:
  1801	        raise MintError(
  1802	            f"postcollection_evidence_mismatch: {label} bracket binding schema mismatch"
  1803	        )
  1804	    if binding.get("schema_version") != V2_BRACKET_BINDING_SCHEMA:
  1805	        raise MintError(
  1806	            f"postcollection_evidence_mismatch: {label} bracket binding version mismatch"
  1807	        )
  1808	    if binding.get("ledger_schema") != "joulewise.calibration_observation_ledger.v1":
  1809	        raise MintError(
  1810	            f"postcollection_evidence_mismatch: {label} bracket ledger schema mismatch"
  1811	        )
  1812	    observed_binding_digest = _canonical_json_sha256(
  1813	        {key: value for key, value in binding.items() if key != "binding_digest"}
  1814	    )
  1815	    if binding.get("binding_digest") != observed_binding_digest:
  1816	        raise MintError(
  1817	            f"postcollection_evidence_mismatch: {label} binding digest mismatch"
  1818	        )
  1819	    for field, expected in (
  1820	        ("plan_id", producer["plan"]["plan_id"]),
  1821	        ("plan_sha256", producer["plan"]["sha256"]),
  1822	        ("evidence_root_id", producer["evidence_root_id"]),
  1823	        ("runs_root", str(inputs.evidence_root.resolve(strict=False))),
  1824	    ):
  1825	        if binding.get(field) != expected:
  1826	            raise MintError(
  1827	            f"postcollection_evidence_mismatch: {label} binding {field} mismatch"
  1828	        )
  1829	    for field in ("session_id", "window_id"):
  1830	        if not isinstance(binding.get(field), str) or not binding[field]:
  1831	            raise MintError(
  1832	                f"postcollection_evidence_mismatch: {label} binding {field} mismatch"
  1833	            )
  1834	    _sha256(
  1835	        binding.get("capability_receipt_digest"),
  1836	        f"{label}.capability_receipt_digest",
  1837	    )
  1838	    _sha256(
  1839	        inputs.bracket_binding_sha256,
  1840	        f"{label}.bracket_binding_sha256",
  1841	    )
  1842	    if not bool(_mapping_attribute(ledger_snapshot, "valid")):
  1843	        raise MintError(
  1844	            f"postcollection_evidence_mismatch: {label} ledger snapshot is invalid"
  1845	        )
  1846	    if _mapping_attribute(ledger_snapshot, "ledger_schema") != binding[
  1847	        "ledger_schema"
  1848	    ]:
  1849	        raise MintError(
  1850	            f"postcollection_evidence_mismatch: {label} ledger snapshot schema mismatch"
  1851	        )
  1852	    receipts = _mapping_attribute(ledger_snapshot, "receipts")
  1853	    observations = _mapping_attribute(ledger_snapshot, "observations")
  1854	    sessions = _mapping_attribute(ledger_snapshot, "bracket_session_by_id")
  1855	    if not isinstance(receipts, tuple | list) or not isinstance(
  1856	        observations, tuple | list
  1857	    ):
  1858	        raise MintError(
  1859	            f"postcollection_evidence_mismatch: {label} ledger snapshot is incomplete"
  1860	        )
  1861	    session = (
  1862	        sessions.get(binding["session_id"])
  1863	        if isinstance(sessions, Mapping)
  1864	        else None
  1865	    )
  1866	    if session is None:
  1867	        raise MintError(
  1868	            f"postcollection_evidence_mismatch: {label} bracket session is absent"
  1869	        )
  1870	    for field, expected in (
  1871	        ("state", "finalized"),
  1872	        ("window_id", binding["window_id"]),
  1873	        ("plan_id", binding["plan_id"]),
  1874	        ("plan_sha256", binding["plan_sha256"]),
  1875	        ("evidence_root_id", binding["evidence_root_id"]),
  1876	        ("runs_root", binding["runs_root"]),
  1877	        (
  1878	            "capability_receipt_digest",
  1879	            binding["capability_receipt_digest"],
  1880	        ),
  1881	    ):
  1882	        if _mapping_attribute(session, field) != expected:
  1883	            raise MintError(
  1884	                f"postcollection_evidence_mismatch: {label} bracket session {field} mismatch"
  1885	            )
  1886	    finalized_slots = _mapping_attribute(session, "finalized_slots")
  1887	    if not isinstance(finalized_slots, Mapping) or set(finalized_slots) != {
  1888	        "pre",
  1889	        "post",
  1890	    }:
  1891	        raise MintError(
  1892	            f"postcollection_evidence_mismatch: {label} finalized bracket slots mismatch"
  1893	        )
  1894	    receipt_digests = {
  1895	        row.get("receipt_digest")
  1896	        for row in receipts
  1897	        if isinstance(row, Mapping) and _SHA256_RE.fullmatch(str(row.get("receipt_digest")))
  1898	    }
  1899	    if binding.get("capability_receipt_digest") not in receipt_digests:
  1900	        raise MintError(
  1901	            f"postcollection_evidence_mismatch: {label} capability receipt is absent"
  1902	        )
  1903	    endpoints = binding.get("endpoints")
  1904	    if not isinstance(endpoints, Mapping) or set(endpoints) != {"pre", "post"}:
  1905	        raise MintError(
  1906	            f"postcollection_evidence_mismatch: {label} binding endpoints mismatch"
  1907	        )
  1908	    resolved = []
  1909	    for role in ("pre", "post"):
  1910	        endpoint = endpoints.get(role)
  1911	        if not isinstance(endpoint, Mapping) or set(endpoint) != {
  1912	            "attempt_id",
  1913	            "receipt_digest",
  1914	            "content_digest",
  1915	        }:
  1916	            raise MintError(
  1917	                f"postcollection_evidence_mismatch: {label} {role} endpoint schema mismatch"
  1918	            )
  1919	        _sha256(endpoint.get("receipt_digest"), f"{label}.{role}.receipt_digest")
  1920	        _sha256(endpoint.get("content_digest"), f"{label}.{role}.content_digest")
  1921	        matches = [
  1922	            observation
  1923	            for observation in observations
  1924	            if _mapping_attribute(observation, "attempt_id")
  1925	            == endpoint.get("attempt_id")
  1926	            and _mapping_attribute(observation, "receipt_digest")
  1927	            == endpoint.get("receipt_digest")
  1928	            and _mapping_attribute(observation, "content_id")
  1929	            == endpoint.get("content_digest")
  1930	        ]
  1931	        if len(matches) != 1:
  1932	            raise MintError(
  1933	                f"postcollection_evidence_mismatch: {label} {role} receipt/content mismatch"
  1934	            )
  1935	        observation = matches[0]
  1936	        finalized_observation = finalized_slots.get(role)
  1937	        if any(
  1938	            _mapping_attribute(finalized_observation, field)
  1939	            != _mapping_attribute(observation, field)
  1940	            for field in (
  1941	                "sequence",
  1942	                "attempt_id",
  1943	                "receipt_digest",
  1944	                "content_id",
  1945	            )
  1946	        ):
  1947	            raise MintError(
  1948	                f"postcollection_evidence_mismatch: {label} {role} finalized slot mismatch"
  1949	            )
  1950	        for field, expected in (
  1951	            ("disposition", "valid"),
  1952	            ("bracket_session_id", binding.get("session_id")),
  1953	            ("bracket_slot", role),
  1954	            ("bracket_window_id", binding.get("window_id")),
  1955	            ("bracket_plan_id", producer["plan"]["plan_id"]),
  1956	            ("bracket_plan_sha256", producer["plan"]["sha256"]),
  1957	            ("bracket_evidence_root_id", producer["evidence_root_id"]),
  1958	        ):
  1959	            if _mapping_attribute(observation, field) != expected:
  1960	                raise MintError(
  1961	                    f"postcollection_evidence_mismatch: {label} {role} {field} mismatch"
  1962	                )
  1963	        resolved.append(observation)
  1964	    terminal = binding.get("terminal_head")
  1965	    post_sequence = _mapping_attribute(resolved[1], "sequence")
  1966	    post_receipt = _mapping_attribute(resolved[1], "receipt_digest")
  1967	    if (
  1968	        not isinstance(terminal, Mapping)
  1969	        or set(terminal) != {"sequence", "head_digest", "ledger_schema"}
  1970	        or terminal.get("ledger_schema")
  1971	        != "joulewise.calibration_observation_ledger.v1"
  1972	        or isinstance(terminal.get("sequence"), bool)
  1973	        or terminal.get("sequence") != post_sequence
  1974	        or terminal.get("head_digest") != post_receipt
  1975	        or not isinstance(post_sequence, int)
  1976	        or post_sequence < 1
  1977	        or post_sequence > len(receipts)
  1978	        or not isinstance(receipts[post_sequence - 1], Mapping)
  1979	        or receipts[post_sequence - 1].get("receipt_digest") != post_receipt
  1980	    ):
  1981	        raise MintError(
  1982	            f"postcollection_evidence_mismatch: {label} terminal ledger head mismatch"
  1983	        )
  1984	    return resolved[0], resolved[1]
  1985	
  1986	
  1987	def _v2_gate_producer_inventory(
  1988	    producer: Mapping[str, Any],
  1989	    inputs: V2ProducerInputs,
  1990	) -> None:
  1991	    plan = producer["plan"]
  1992	    plan_id = plan["plan_id"]
  1993	    if inputs.plan_sha256 != plan["sha256"]:
  1994	        raise MintError(f"producer {plan_id!r}: calibration plan sha256 mismatch")
  1995	    if inputs.plan_declared_sha256 != plan["declared_sha256"]:
  1996	        raise MintError(f"producer {plan_id!r}: declared plan sha256 mismatch")
  1997	    if inputs.plan_sidecar_sha256 != plan["sidecar_sha256"]:
  1998	        raise MintError(f"producer {plan_id!r}: plan sidecar sha256 mismatch")
  1999	    if inputs.plan.get("plan_id") != plan_id or inputs.plan.get(
  2000	        "calibration_scope"
  2001	    ) != plan["declared_calibration_scope"]:
  2002	        raise MintError(f"producer {plan_id!r}: calibration plan identity mismatch")
  2003	    acceptance = inputs.calibration_acceptance
  2004	    acceptance_pins = producer["calibration_acceptance"]
  2005	    if (
  2006	        not isinstance(acceptance, Mapping)
  2007	        or acceptance.get("acceptance_id") != acceptance_pins["acceptance_id"]
  2008	        or inputs.calibration_acceptance_sha256
  2009	        != acceptance_pins["artifact_sha256"]
  2010	        or acceptance.get("derivation_sha256")
  2011	        != acceptance_pins["derivation_sha256"]
  2012	        or acceptance.get("schema_version")
  2013	        != acceptance_pins["derivation_rule_id"]
  2014	    ):
  2015	        raise MintError(
  2016	            f"producer {plan_id!r}: calibration acceptance evidence mismatch"
  2017	        )
  2018	    components = [
  2019	        component
  2020	        for cell in inputs.cells.values()
  2021	        for component in (cell.absolute, cell.comparative)
  2022	    ]
  2023	    if not components:
  2024	        raise MintError(f"producer {plan_id!r}: no authenticated components")
  2025	    extraction_sha256s = {component.spec_sha256 for component in components}
  2026	    if extraction_sha256s != {producer["extraction_spec"]["sha256"]}:
  2027	        raise MintError(f"producer {plan_id!r}: extraction spec inventory mismatch")
  2028	    unique_members = {
  2029	        member.bundle_id for component in components for member in component.members
  2030	    }
  2031	    if len(unique_members) != producer["extraction_spec"]["member_count"]:
  2032	        raise MintError(f"producer {plan_id!r}: extraction member inventory mismatch")
  2033	    model_hashes = {
  2034	        component.source_regime.get("stack_identity", {}).get(
  2035	            "model_artifact_sha256"
  2036	        )
  2037	        for component in components
  2038	    }
  2039	    runtime_hashes = {
  2040	        component.source_regime.get("stack_identity_sha256")
  2041	        for component in components
  2042	    }
  2043	    config_hashes = {
  2044	        component.scientific_config_identity_sha256 for component in components
  2045	    }
  2046	    runtime_pins = producer["model_runtime_config"]
  2047	    if model_hashes != {runtime_pins["model_artifact_sha256"]}:
  2048	        raise MintError(f"producer {plan_id!r}: model artifact inventory mismatch")
  2049	    if runtime_hashes != {runtime_pins["runtime_identity_sha256"]}:
  2050	        raise MintError(f"producer {plan_id!r}: runtime identity inventory mismatch")
  2051	    if config_hashes != {runtime_pins["config_set_sha256"]}:
  2052	        raise MintError(f"producer {plan_id!r}: config-set inventory mismatch")
  2053	
  2054	
  2055	def _v2_gate_postcollection(
  2056	    *,
  2057	    producer: Mapping[str, Any],
  2058	    cell_pins: Mapping[str, Any],
  2059	    cell_inputs: V2CellComponents,
  2060	    producer_inputs: V2ProducerInputs,
  2061	    ledger_snapshot: Any,
  2062	) -> None:
  2063	    post = cell_pins["postcollection"]
  2064	    pre, post_observation = _v2_authenticate_bracket_binding(
  2065	        producer=producer,
  2066	        inputs=producer_inputs,
  2067	        ledger_snapshot=ledger_snapshot,
  2068	    )
  2069	    expected_binding_sha256 = post["bracket_binding_sha256"]
  2070	    _require_postcollection_evidence_equal(
  2071	        "bracket_binding_sha256",
  2072	        expected_binding_sha256,
  2073	        producer_inputs.bracket_binding_sha256,
  2074	        source="supplied bracket-binding artifact bytes",
  2075	    )
  2076	    binding = producer_inputs.bracket_binding
  2077	    endpoint_fields = {
  2078	        "pre": ("pre_receipt_sha256", "pre_content_sha256"),
  2079	        "post": ("post_receipt_sha256", "post_content_sha256"),
  2080	    }
  2081	    for role, observation in (("pre", pre), ("post", post_observation)):
  2082	        receipt_field, content_field = endpoint_fields[role]
  2083	        _require_postcollection_evidence_equal(
  2084	            receipt_field,
  2085	            post[receipt_field],
  2086	            _mapping_attribute(observation, "receipt_digest"),
  2087	            source=f"authenticated ledger {role} observation",
  2088	        )
  2089	        _require_postcollection_evidence_equal(
  2090	            content_field,
  2091	            post[content_field],
  2092	            _mapping_attribute(observation, "content_id"),
  2093	            source=f"authenticated ledger {role} observation",
  2094	        )
  2095	    _require_postcollection_evidence_equal(
  2096	        "terminal_ledger_head_sha256",
  2097	        post["terminal_ledger_head_sha256"],
  2098	        binding["terminal_head"]["head_digest"],
  2099	        source="authenticated bracket-binding terminal head",
  2100	    )
  2101	    try:
  2102	        observed_drift = abs(
  2103	            _decimal_text(
  2104	                _mapping_attribute(pre, "exact_bound_lexeme_s"),
  2105	                "ledger pre exact_bound_lexeme_s",
  2106	            )
  2107	            - _decimal_text(
  2108	                _mapping_attribute(post_observation, "exact_bound_lexeme_s"),
  2109	                "ledger post exact_bound_lexeme_s",
  2110	            )
  2110	            )
  2111	        )
  2112	    except (InvalidOperation, MintError) as exc:
  2113	        raise MintError(
  2114	            "postcollection_evidence_mismatch: ledger endpoint drift is not exact Decimal evidence"
  2115	        ) from exc
  2116	    _require_postcollection_evidence_equal(
  2117	        "observed_drift_s",
  2118	        _decimal_text(post["observed_drift_s"], "postcollection.observed_drift_s"),
  2119	        observed_drift,
  2120	        source="authenticated ledger endpoint bounds",
  2121	    )
  2122	    actual_components = (cell_inputs.absolute, cell_inputs.comparative)
  2123	    for component in actual_components:
  2124	        _require_postcollection_evidence_equal(
  2125	            "extraction_report_sha256",
  2126	            post["extraction_report_sha256"],
  2127	            component.report_sha256,
  2128	            source=f"supplied {component.kind} extraction-report artifact bytes",
  2129	        )
  2130	    records = [
  2131	        _v2_extraction_postcollection_record(
  2132	            component,
  2133	            cell_pins["cell_id"],
  2134	            label=f"{cell_pins['cell_id']}.{component.kind}",
  2135	        )
  2136	        for component in actual_components
  2137	    ]
  2138	    if records[0] != records[1]:
  2139	        raise MintError(
  2140	            "postcollection_evidence_mismatch: component extraction reports disagree"
  2141	        )
  2142	    report_record = records[0]
  2143	    for name in (
  2144	        "observed_drift_s",
  2145	        "applied_allowance_s",
  2146	        "absolute_floor_full_precision",
  2147	        "comparative_floor_full_precision",
  2148	        "operative_floor_full_precision",
  2149	        "absolute_floor_six_decimal",
  2150	        "comparative_floor_six_decimal",
  2151	        "operative_floor_six_decimal",
  2152	    ):
  2153	        _require_postcollection_evidence_equal(
  2154	            name,
  2155	            post[name],
  2156	            report_record[name],
  2157	            source="authenticated extraction-report record",
  2158	        )
  2159	    actual_values = (
  2160	        cell_inputs.absolute.cell.get("floor", {}).get(
  2161	            "drift_widened_guarded_floor_j"
  2162	        ),
  2163	        cell_inputs.comparative.cell.get("floor", {}).get(
  2164	            "drift_widened_guarded_floor_j"
  2165	        ),
  2166	    )
  2167	    expected_values = (
  2168	        _decimal_text(
  2169	            post["absolute_floor_full_precision"],
  2170	            "postcollection.absolute_floor_full_precision",
  2171	        ),
  2172	        _decimal_text(
  2173	            post["comparative_floor_full_precision"],
  2174	            "postcollection.comparative_floor_full_precision",
  2175	        ),
  2176	    )
  2177	    for name, actual, expected in zip(
  2178	        ("absolute", "comparative"), actual_values, expected_values
  2179	    ):
  2180	        if isinstance(actual, bool) or not isinstance(actual, int | float):
  2181	            raise MintError(
  2182	                f"postcollection_evidence_mismatch: {name} extraction value is not numeric"
  2183	            )
  2184	        if Decimal(str(actual)) != expected:
  2185	            raise MintError(
  2186	                f"postcollection_evidence_mismatch: {name} full-precision value mismatch"
  2187	            )
  2188	
  2189	
  2190	def _v2_allowed_families(
  2191	    supplied: Sequence[Mapping[str, Any]],
  2192	    pins: Sequence[Mapping[str, Any]],
  2193	    *,
  2194	    label: str,
  2195	) -> list[Mapping[str, Any]]:
  2196	    expected = [
  2197	        (row["condition_family_id"], row["condition_family_sha256"])
  2198	        for row in pins
  2199	    ]
  2200	    observed = []
  2201	    normalized = []
  2202	    from joulewise.detection_floor import (
  2203	        CONDITION_FAMILY_DOMAIN,
  2204	        canonical_domain_sha256,
  2205	    )
  2206	
  2207	    for index, row in enumerate(supplied):
  2208	        if not isinstance(row, Mapping):
  2209	            raise MintError(f"{label}[{index}] must be an object")
  2210	        definition = row.get("condition_family_definition")
  2211	        family_id = row.get("condition_family_id")
  2212	        family_sha256 = row.get("condition_family_sha256")
  2213	        if not isinstance(definition, Mapping) or not isinstance(family_id, str):
  2214	            raise MintError(f"{label}[{index}] is incomplete")
  2215	        if canonical_domain_sha256(CONDITION_FAMILY_DOMAIN, definition) != (
  2216	            family_sha256
  2217	        ):
  2218	            raise MintError(f"{label}[{index}] condition-family hash mismatch")
  2219	        observed.append((family_id, family_sha256))
  2220	        normalized.append(dict(row))
  2221	    if observed != expected:
  2222	        raise MintError(f"{label} does not match the transport allowlist pins")
  2223	    return normalized
  2224	
  2225	
  2226	def _v2_pre_registration_gate(
  2227	    *,
  2228	    core: ModuleType,
  2229	    producer: Mapping[str, Any],
  2230	    cell_pins: Mapping[str, Any],
  2231	    plan: Mapping[str, Any],
  2232	    absolute: Any,
  2233	    comparative: Any,
  2234	) -> Mapping[str, Any]:
  2235	    plan_pins = producer["plan"]
  2236	    if absolute.order_manifest.get("calibration_plan_sha256") != plan_pins[
  2237	        "sha256"
  2238	    ] or comparative.order_manifest.get("calibration_plan_sha256") != plan_pins[
  2239	        "sha256"
  2240	    ]:
  2241	        raise MintError("v2 pre-registration gate: order-manifest plan sha mismatch")
  2242	    if absolute.order_manifest.get("plan_id") != plan.get(
  2243	        "plan_id"
  2244	    ) or comparative.order_manifest.get("plan_id") != plan.get("plan_id"):
  2245	        raise MintError("v2 pre-registration gate: order-manifest plan id mismatch")
  2246	    absolute_binding = core._definition_binding(absolute)
  2247	    comparative_bindings = comparative.spec_cell.get(
  2248	        "condition_family_definitions"
  2249	    )
  2250	    if (
  2251	        not isinstance(comparative_bindings, Mapping)
  2252	        or comparative_bindings.get("A") != comparative_bindings.get("B")
  2253	        or absolute_binding != comparative_bindings.get("A")
  2254	        or absolute_binding.get("condition_family_id")
  2255	        != cell_pins["condition_family_id"]
  2520	        )
  2521	        if component_errors:
  2522	            raise MintError(
  2523	                f"constructed v2 component artifact is invalid: {component_errors[0]}"
  2524	            )
  2525	        component_artifacts.append(component)
  2526	        all_cells.extend(copy.deepcopy(producer_cells))
  2527	        all_groups.extend(copy.deepcopy(producer_groups))
  2528	        producer_plan_records.append(
  2529	            {
  2530	                "plan_id": plan_id,
  2531	                "declared_calibration_scope": plan_pins[
  2532	                    "declared_calibration_scope"
  2533	                ],
  2534	                "relative_path": plan_pins["relative_path"],
  2535	                "sha256": plan_pins["sha256"],
  2536	            }
  2537	        )
  2538	
  2539	    aggregate = pinset.value["aggregate"]
  2540	    implementation = copy.deepcopy(
  2541	        component_artifacts[0]["provenance"]["implementation"]
  2542	    )
  2543	    artifact = {
  2544	        **copy.deepcopy(component_artifacts[0]),
  2545	        "artifact_id": aggregate["artifact_id"],
  2546	        "calibration_scope": aggregate["calibration_scope"],
  2547	        "source_class": aggregate["source_class"],
  2548	        "provenance": {
  2549	            "calibration_plan": {
  2550	                "plan_id": aggregate["plan_set_id"],
  2551	                "declared_calibration_scope": "production_window",
  2552	                "relative_path": Path(pinset_path).name,
  2553	                "sha256": aggregate["producer_set_sha256"],
  2554	            },
  2555	            "producer_calibration_plans": producer_plan_records,
  2556	            "mint_tool_version": V2_MINT_TOOL_VERSION,
  2557	            "implementation": implementation,
  2558	        },
  2559	        "cells": all_cells,
  2560	        "transport_groups": all_groups,
  2561	    }
  2562	    errors = validate_floor_artifact(
  2563	        artifact=artifact,
  2564	        pinset_path=pinset_path,
  2565	        pinset_sha256=pinset_sha256,
  2566	        _skip_v2_hash_binding=True,
  2567	    )
  2568	    if errors:
  2569	        raise MintError(f"constructed v2 aggregate artifact is invalid: {errors[0]}")
  2570	    return artifact, tuple(component_artifacts)
  2571	
  2572	
  2573	def _validate_v2_artifact_binding(
  2574	    artifact: Mapping[str, Any],
  2575	    pinset: V2Pinset,
  2576	) -> list[str]:
  2577	    errors: list[str] = []
  2578	    value = pinset.value
  2579	    aggregate = value["aggregate"]
  2580	    try:
  2581	        _validate_v2_pin_hashes(pinset)
  2582	    except MintError as exc:
  2583	        errors.append(f"artifact.pinset: {exc}")
  2584	    if artifact.get("artifact_id") != aggregate["artifact_id"]:
  2585	        errors.append("artifact: aggregate artifact_id mismatch")
  2586	    provenance = artifact.get("provenance")
  2587	    expected_producer_plans = [
  2588	        {
  2589	            "plan_id": producer["plan"]["plan_id"],
  2590	            "declared_calibration_scope": producer["plan"][
  2591	                "declared_calibration_scope"
  2592	            ],
  2593	            "relative_path": producer["plan"]["relative_path"],
  2594	            "sha256": producer["plan"]["sha256"],
  2595	        }
  2596	        for producer in value["producer_plans"]
  2597	    ]
  2598	    if not isinstance(provenance, Mapping):
  2599	        errors.append("artifact.provenance: v2 aggregate provenance is missing")
  2600	    else:
  2601	        expected_aggregate_plan = {
  2602	            "plan_id": aggregate["plan_set_id"],
  2603	            "declared_calibration_scope": "production_window",
  2604	            "relative_path": Path("pinset.json").name,
  2605	            "sha256": aggregate["producer_set_sha256"],
  2606	        }
  2607	        aggregate_plan = provenance.get("calibration_plan")
  2608	        if not isinstance(aggregate_plan, Mapping) or any(
  2609	            aggregate_plan.get(field) != expected
  2610	            for field, expected in expected_aggregate_plan.items()
  2611	            if field != "relative_path"
  2612	        ):
  2613	            errors.append("artifact.provenance: aggregate plan-set pin mismatch")
  2614	        if provenance.get("producer_calibration_plans") != expected_producer_plans:
  2615	            errors.append("artifact.provenance: producer plan pins mismatch")
  2616	        if provenance.get("mint_tool_version") != V2_MINT_TOOL_VERSION:
  2617	            errors.append("artifact.provenance: v2 mint-tool identity mismatch")
  2618	    cells = artifact.get("cells")
  2619	    groups = artifact.get("transport_groups")
  2620	    if not isinstance(cells, list) or not isinstance(groups, list):
  2621	        return [*errors, "artifact: v2 cells/transport_groups are not arrays"]
  2622	    if [cell.get("cell_id") for cell in cells if isinstance(cell, Mapping)] != (
  2623	        aggregate["cell_ids"]
  2624	    ):
  2625	        errors.append("artifact: four-cell order does not match aggregate pins")
  2626	    group_by_id = {
  2627	        group.get("transport_group_id"): group
  2628	        for group in groups
  2629	        if isinstance(group, Mapping)
  2630	    }
  2631	    cell_by_id = {
  2632	        cell.get("cell_id"): cell
  2633	        for cell in cells
  2634	        if isinstance(cell, Mapping)
  2635	    }
  2636	
  2637	    for producer in value["producer_plans"]:
  2638	        for cell_pin in producer["cells"]:
  2639	            cell = cell_by_id.get(cell_pin["cell_id"])
  2640	            if not isinstance(cell, Mapping):
  2641	                continue
  2642	            key = cell.get("key", {})
  2643	            for field in (
  2644	                "metric",
  2645	                "window_class",
  2646	                "condition_family_id",
  2647	                "condition_family_sha256",
  2648	            ):
  2649	                expected = (
  2650	                    cell_pin[field]
  2651	                    if field in cell_pin
  2652	                    else cell_pin.get(field)
  2653	                )
  2654	                if key.get(field) != expected:
  2655	                    errors.append(f"cells[{cell_pin['cell_id']}]: {field} pin mismatch")
  2656	            post = cell_pin["postcollection"]
  2657	            for artifact_field, pin_field, component_name in (
  2658	                (
  2659	                    "floor_abs_j",
  2660	                    "absolute_floor_full_precision",
  2661	                    "absolute",
  2662	                ),
  2663	                (
  2664	                    "floor_cmp_j",
  2665	                    "comparative_floor_full_precision",
  2666	                    "comparative",
  2667	                ),
  2668	                (
  2669	                    "floor_gate_j",
  2670	                    "operative_floor_full_precision",
  2671	                    "operative",
  2672	                ),
  2673	            ):
  2674	                actual = cell.get(artifact_field)
  2675	                if (
  2676	                    isinstance(actual, bool)
  2677	                    or not isinstance(actual, int | float)
  2678	                    or not math.isfinite(float(actual))
  2679	                    or Decimal(str(actual)) != Decimal(post[pin_field])
  2680	                ):
  2681	                    errors.append(
  2682	                        f"cells[{cell_pin['cell_id']}]: {component_name} "
  2683	                        "full-precision pin mismatch"
  2684	                    )
  2685	            cell_provenance = cell.get("provenance", {})
  2686	            roots = {
  2687	                row.get("evidence_root_id")
  2688	                for row in cell_provenance.values()
  2689	                if isinstance(row, Mapping)
  2690	            }
  2691	            if roots != {producer["evidence_root_id"]}:
  2692	                errors.append(f"cells[{cell_pin['cell_id']}]: evidence-root pin mismatch")
  2693	            group = group_by_id.get(cell_pin["transport_group_id"])
  2694	            if not isinstance(group, Mapping) or group.get("source_cell_ids") != [
  2695	                cell_pin["cell_id"]
  2696	            ]:
  2697	                errors.append(
  2698	                    f"cells[{cell_pin['cell_id']}]: transport must remain independently stack-scoped"
  2699	                )
  2700	            elif [
1002:                "declared_calibration_scope": "production_window",
1003:                "artifact_calibration_scope": "production_window",
1005:            "evidence_root_id": evidence_root_id,
1035:            evidence_root=evidence_root,
1052:            "calibration_scope": "production_window",
1083:# Independent golden constants. They are regenerated only by an explicit
1096:CLI_COMPONENT_SHA256S = (
1102:def _repair_v2_pinset_self_hashes(pinset: dict) -> None:
1103:    """Repair only pinset self-hashes with an independent JSON oracle."""
1186:        evidence_root = root / f"{plan_id}-root"
1187:        evidence_root.mkdir()
1188:        binding, receipts, observations, session = _synthetic_bracket_evidence(
1192:            evidence_root_id=producer["evidence_root_id"],
1193:            runs_root=evidence_root,
1256:                    "evidence_root": str(evidence_root),
1264:                        str(evidence_root.resolve()),
1359:                str(paths.evidence_root.resolve()),
1363:                raise core.MintError("unexpected component cell/evidence root")
1386:        core.bind_floor_artifact_evidence = lambda *_args, **_kwargs: {}
1392:        CLI_COMPONENT_SHA256S,
1396:    _repair_v2_pinset_self_hashes(pinset)
1401:class PinsetTests(unittest.TestCase):
1402:    def test_mint1_pinset_is_exactly_the_original_hard_pin_set(self) -> None:
1406:        self.assertEqual(pinset.plan.sha256, mint1.PLAN_SHA256)
1407:        self.assertEqual(pinset.artifact.cell_id, mint1.CELL_ID)
1408:        self.assertEqual(
1412:        self.assertEqual(
1416:        self.assertEqual(
1421:    def test_pinset_digest_mismatch_refuses(self) -> None:
1422:        with self.assertRaisesRegex(generalized.MintError, "sha256 mismatch"):
1425:    def test_pinset_missing_or_extra_fields_refuse(self) -> None:
1437:                with self.subTest(label=label):
1439:                    with self.assertRaisesRegex(
1444:    def test_operative_floor_pin_requires_six_decimal_string(self) -> None:
1449:            with self.assertRaisesRegex(
1454:    def test_pinset_cannot_weaken_fixed_decode_contract(self) -> None:
1463:                with self.subTest(label=label):
1470:                    with self.assertRaisesRegex(
1476:class V2PinsetAndMintTests(unittest.TestCase):
1477:    def test_synthetic_hash_oracle_is_literal_and_builder_independent(
1478:        self,
1485:                _repair_v2_pinset_self_hashes,
1489:        self.assertNotIn("generalized._", helper_source)
1490:        self.assertNotIn("generalized._build_v2_artifacts", helper_source)
1491:        self.assertNotIn("generalized._artifact_sha256", helper_source)
1492:        self.assertTrue(
1495:        self.assertTrue(
1498:        self.assertNotEqual(SYNTHETIC_PRODUCER_SET_SHA256, "0" * 64)
1500:    def test_desk_stage_is_structurally_disjoint_and_cannot_mint(self) -> None:
1530:        self.assertNotEqual(
1540:            with self.assertRaisesRegex(
1545:    def test_synthetic_two_plan_four_cell_mint_passes(self) -> None:
1558:            self.assertEqual(
1566:        self.assertEqual(len(artifact["cells"]), 4)
1567:        self.assertEqual(len(artifact["transport_groups"]), 4)
1568:        self.assertEqual(
1572:        self.assertTrue(
1581:    def test_v2_mint_does_not_render_or_round_floor_literals(self) -> None:
1589:        self.assertEqual(
1621:        self.assertEqual(len(artifact["cells"]), 4)
1623:    def test_fabricated_postcollection_pins_refuse_after_self_hash_repair(
1624:        self,
1632:            custody_hashes = (
1646:                    for hash_index, field in enumerate(custody_hashes):
1648:                            producer_index * len(custody_hashes)
1655:            _repair_v2_pinset_self_hashes(fabricated)
1657:            with self.assertRaisesRegex(
1659:                "postcollection_evidence_mismatch",
1670:    def test_floor_rendering_and_extraction_record_mismatches_refuse(self) -> None:
1699:                with self.subTest(field=field):
1704:                    _repair_v2_pinset_self_hashes(candidate)
1708:                    with self.assertRaisesRegex(
1721:    def test_coordinated_report_and_pin_change_refuses_against_floor_evidence(
1722:        self,
1770:            coordinated_inputs = {
1774:            _repair_v2_pinset_self_hashes(candidate)
1776:            with self.assertRaisesRegex(
1783:                    producer_inputs=coordinated_inputs,
1789:    def test_per_component_consumption_semantics_pin_is_evidence_bound(
1790:        self,
1801:            _repair_v2_pinset_self_hashes(candidate)
1803:            with self.assertRaisesRegex(
1816:    def test_false_producer_inventory_pins_refuse_after_self_hash_repair(
1817:        self,
1845:                    "calibration acceptance evidence mismatch",
1849:                with self.subTest(label=label):
1852:                    _repair_v2_pinset_self_hashes(candidate)
1856:                    with self.assertRaisesRegex(generalized.MintError, message):
1866:    def test_v2_cli_requires_an_explicit_input_manifest(self) -> None:
1888:            self.assertEqual(exit_code, 2)
1889:            self.assertIn("requires --v2-input-manifest", stderr.getvalue())
1891:    def test_production_cli_mints_and_names_every_custody_mismatch(self) -> None:
1922:                self.assertEqual(
1928:            self.assertTrue((root / "correct-floor.json").is_file())
1929:            self.assertTrue((root / "correct-single-count.txt").is_file())
1945:                with self.subTest(field=field):
1949:                    _repair_v2_pinset_self_hashes(candidate)
1965:                    self.assertEqual(exit_code, 2)
1966:                    self.assertIn(field, stderr.getvalue())
1967:                    self.assertFalse((root / f"{field}-floor.json").exists())
1968:                    self.assertFalse(
1972:    def test_v2_input_manifest_routes_all_authenticated_evidence_files(
1973:        self,
2022:                producer_evidence_root = root / f"{plan_id}-root"
2023:                producer_evidence_root.mkdir()
2025:                    producer_evidence_root.resolve(strict=False)
2051:                            "evidence_root": str(producer_evidence_root),
2094:            _repair_v2_pinset_self_hashes(pinset)
2110:            evidence_core = SimpleNamespace(
2121:                self.assertEqual(
2125:                self.assertEqual(
2129:                self.assertIs(
2143:                    return_value=evidence_core,
2161:        self.assertEqual(set(authenticated), set(source_inputs))
2162:        self.assertEqual(len(roots), 2)
2163:        self.assertIs(observed_snapshot, ledger_snapshot)
2164:        self.assertEqual(component_core._authenticate_component.call_count, 8)
2165:        evidence_core.load_calibration_acceptance_bound.assert_called_once_with(
2168:        evidence_core.load_calibration_ledger_snapshot.assert_called_once()
2170:    def test_missing_unresolved_and_derived_literal_attempts_refuse(self) -> None:
2192:                with self.subTest(label=label):
2196:                    with self.assertRaisesRegex(generalized.MintError, message):
2201:    def test_sum_allowance_and_metric_refusal_vectors(self) -> None:
2243:                with self.subTest(label=label):
2247:                    with self.assertRaisesRegex(generalized.MintError, message):
2252:    def test_v2_decimal_pins_require_plain_unsigned_strings(self) -> None:
2262:                with self.subTest(label=label):
2272:                    with self.assertRaisesRegex(
2280:    def test_retired_literal_refuses_explicitly(self) -> None:
2289:            with self.assertRaisesRegex(
2294:    def test_aggregate_and_component_hash_mismatches_refuse(self) -> None:
2304:            with self.assertRaisesRegex(
2328:            with self.assertRaisesRegex(
2349:            _repair_v2_pinset_self_hashes(component_bad)
2353:            with self.assertRaisesRegex(
2365:    def test_shared_v2_projection_rejects_nested_extra_fields(self) -> None:
2379:        _repair_v2_pinset_self_hashes(candidate)
2380:        self.assertIsNone(
2384:    def test_malformed_v2_producer_provenance_returns_errors_not_crash(
2385:        self,
2408:        self.assertTrue(any("plan_id" in error for error in errors), errors)
2411:class GeneralizedMintTests(unittest.TestCase):
2412:    def test_mint1_builder_path_is_byte_identical(self) -> None:
2444:        self.assertEqual(actual_bytes, expected_bytes)
2446:    def test_7b_shaped_gate_build_and_validator_path_passes(self) -> None:
2448:        self.assertEqual(validate_extraction_spec(absolute.spec), [])
2490:        self.assertEqual(validation_errors, [])
2491:        self.assertEqual(artifact["calibration_scope"], "production_window")
2492:        self.assertEqual(
2496:            "production_window",
2498:        self.assertEqual(
2502:        self.assertEqual(
2507:        self.assertEqual(
2508:            provenance["absolute"]["evidence_root_id"],
2511:        self.assertEqual(
2512:            provenance["comparative"]["evidence_root_id"],
2516:    def test_7b_mismatched_operative_pin_refuses(self) -> None:
2522:            with self.assertRaisesRegex(
2538:    def test_7b_mismatched_plan_and_manifest_pins_refuse(self) -> None:
2560:                with self.subTest(label=label):
2561:                    with self.assertRaisesRegex(generalized.MintError, message):
2572:class FullPathTests(unittest.TestCase):
2576:            evidence_root=root / "unused-root",
2583:        self,
2594:        dummy = self._dummy_inputs(root)
2621:    def test_mint1_full_path_is_byte_identical_to_review_pinned_mint_core(
2622:        self,
2677:                        evidence_root_id="a10",
2678:                        evidence_root=absolute_inputs.evidence_root,
2686:                        evidence_root_id="window_c",
2687:                        evidence_root=comparative_inputs.evidence_root,
2702:            with self._patched_fresh_loader():
2703:                self._call_generalized(
2713:            self.assertEqual(actual_floor.read_bytes(), expected_floor.read_bytes())
2714:            self.assertEqual(
2718:    def test_truthful_7b_fixture_mints_through_full_path(self) -> None:
2729:            evidence_root = root / SEVEN_B_EVIDENCE_ROOT_ID
2734:                evidence_root=evidence_root,
2740:                evidence_root=evidence_root,
2745:            with self._patched_fresh_loader():
2746:                artifact = self._call_generalized(
2756:            self.assertEqual(
2765:            self.assertEqual(
2767:                    provenance["absolute"]["evidence_root_id"],
2768:                    provenance["comparative"]["evidence_root_id"],
2773:    def test_bad_pinset_digest_refuses_at_full_path(self) -> None:
2776:            with self.assertRaisesRegex(generalized.MintError, "sha256 mismatch"):
2777:                self._call_generalized(
2783:    def test_duplicate_nonfinite_and_malformed_json_refuse_at_full_path(self) -> None:
2801:                with self.subTest(label=label):
2808:                    with self.assertRaisesRegex(
2811:                        self._call_generalized(
2817:    def test_every_pinset_key_is_required_at_full_path(self) -> None:
2830:                with self.subTest(path=".".join(path_parts)):
2837:                    with self.assertRaisesRegex(
2840:                        self._call_generalized(
2846:    def test_binding_and_exclusive_write_refuse_at_full_path(self) -> None:
2865:                self._patched_fresh_loader(),
2866:                self.assertRaisesRegex(
2870:                self._call_generalized(
2881:            with self._patched_fresh_loader():
2882:                self._call_generalized(
2894:                self._patched_fresh_loader(),
2895:                self.assertRaisesRegex(generalized.MintError, "overwrite"),
2897:                self._call_generalized(
2907:            self.assertEqual(floor.read_bytes(), original)
2910:class CoreCompatibilityTests(unittest.TestCase):
2911:    def test_mint_floor_artifact_signature_is_review_pinned(self) -> None:
2923:        self.assertEqual(
2927:        self.assertEqual(
2932:    def test_fresh_core_is_removed_from_sys_modules_after_load(self) -> None:
2934:        self.assertNotIn(core.__name__, sys.modules)
2936:    def test_missing_or_renamed_core_symbol_refuses_loudly(self) -> None:
2937:        with self.assertRaisesRegex(
2942:    def test_core_signature_drift_refuses_loudly(self) -> None:
2945:        with self.assertRaisesRegex(
2950:    def test_repr_spoofed_sentinel_default_refuses_loudly(self) -> None:
2952:            def __repr__(self) -> str:
2959:        self.assertEqual(
2963:        with self.assertRaisesRegex(

exec
/bin/zsh -lc "nl -ba scripts/mint_floor_artifact_generalized.py | sed -n '1,280p'; nl -ba scripts/mint_floor_artifact_generalized.py | sed -n '1690,2095p'; nl -ba scripts/mint_floor_artifact_generalized.py | sed -n '2090,2275p'; nl -ba scripts/mint_floor_artifact_generalized.py | sed -n '2730,3020p'" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u3
 succeeded in 0ms:
     1	#!/usr/bin/env python3
     2	"""Mint a floor artifact with a digest-authenticated per-plan pinset.
     3	
     4	This is the generalized sibling of ``mint_floor_artifact.py``.  It reuses
     5	that mint's authentication, construction, binding, validation, and exclusive
     6	write path through the review-pinned mint-core interface.  Every value that
     7	the original tool hard-coded is required in one exact-schema JSON pinset,
     8	whose exact file bytes must match a separately supplied SHA-256.
     9	"""
    10	
    11	from __future__ import annotations
    12	
    13	import argparse
    14	import copy
    15	import hashlib
    16	import importlib.util
    17	import inspect
    18	import itertools
    19	import json
    20	import math
    21	import re
    22	import stat
    23	import sys
    24	from dataclasses import dataclass, replace
    25	from decimal import Decimal, InvalidOperation, ROUND_HALF_EVEN, localcontext
    26	from pathlib import Path
    27	from types import ModuleType
    28	from typing import Any, Callable, Mapping, Sequence
    29	
    30	
    31	REPO_ROOT = Path(__file__).resolve().parents[1]
    32	if str(REPO_ROOT) not in sys.path:
    33	    sys.path.insert(0, str(REPO_ROOT))
    34	
    35	from joulewise.whole_window import (  # noqa: E402
    36	    MAX_BRACKET_CONSUMPTION_SEMANTICS_ID,
    37	    MINTED_CONSUMPTION_SEMANTICS_ID,
    38	    SALVAGE_DANGLER_CONSUMPTION_SEMANTICS_ID,
    39	)
    40	
    41	
    42	PINSET_SCHEMA_VERSION = "joulewise.floor_mint_pinset.v1"
    43	PINSET_SCHEMA_VERSION_V2 = "joulewise.floor_mint_pinset.v2"
    44	PIN_REQUIREMENTS_SCHEMA_VERSION_V2 = "joulewise.floor_mint_pin_requirements.v2"
    45	V2_MINT_TOOL_VERSION = "joulewise.floor_mint.generalized.v2"
    46	V2_ALLOWANCE_RULE = "max(observed_drift_s,0.010818)"
    47	V2_BRACKET_SCREEN_S = "0.010818"
    48	V2_CELL_COMPOSITION_RULE = "componentwise_max_never_sum.v1"
    49	V2_CONSUMER_FLOOR_RULE = "cross_stack_armwise_max.v1"
    50	V2_EXTRACTION_POSTCOLLECTION_SCHEMA = (
    51	    "joulewise.floor_mint_extraction_postcollection.v2"
    52	)
    53	V2_BRACKET_BINDING_SCHEMA = "joulewise.calibration_bracket_binding.v1"
    54	RETIRED_OPERATIVE_FLOOR_LITERAL = "7.377086"
    55	_ORIGINAL_MINT_PATH = Path(__file__).with_name("mint_floor_artifact.py")
    56	_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
    57	_DECIMAL_RE = re.compile(r"^(?:0|[1-9][0-9]*)(?:\.[0-9]+)?$")
    58	_SIX_DECIMAL_RE = re.compile(r"^(?:0|[1-9][0-9]*)\.[0-9]{6}$")
    59	_SIX_DECIMAL_QUANTUM = Decimal("0.000001")
    60	_EVIDENCE_ROOT_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
    61	_SEMANTICS_IDS = {
    62	    MINTED_CONSUMPTION_SEMANTICS_ID,
    63	    MAX_BRACKET_CONSUMPTION_SEMANTICS_ID,
    64	    SALVAGE_DANGLER_CONSUMPTION_SEMANTICS_ID,
    65	}
    66	_CORE_SEQUENCE = itertools.count()
    67	_CORE_CONFIG_GLOBALS = frozenset(
    68	    {
    69	        "MINT_TOOL_VERSION",
    70	        "CELL_ID",
    71	        "TRANSPORT_GROUP_ID",
    72	        "CONDITION_FAMILY_ID",
    73	        "CONDITION_FAMILY_SHA256",
    74	        "PLAN_SHA256",
    75	        "A10_EVALUATION_BASIS_SHA256",
    76	        "WINDOW_C_EVALUATION_BASIS_SHA256",
    77	        "A10_EVALUATION_BASIS_MEMBERS",
    78	        "WINDOW_C_EVALUATION_BASIS_MEMBERS",
    79	        "A10_SPEC_MEMBERS",
    80	        "WINDOW_C_SPEC_MEMBERS",
    81	        "EXPECTED_ABSOLUTE_N",
    82	        "EXPECTED_COMPARATIVE_N_BLOCKS",
    83	        "A10_DRIFT_ALLOWANCE_J",
    84	        "WINDOW_C_DRIFT_ALLOWANCE_J",
    85	        "EXPECTED_OPERATIVE_FLOOR_TEXT",
    86	        "A10_ORDER_MANIFEST_ID",
    87	        "WINDOW_C_ORDER_MANIFEST_ID",
    88	        "A10_CELL_ID",
    89	        "WINDOW_C_CELL_ID",
    90	        "METRIC",
    91	        "WINDOW_CLASS",
    92	        "TARGET_PRECHECK_PATH",
    93	        "CALIBRATION_SCOPE",
    94	        "PLAN_DECLARED_SCOPE",
    95	        "SOURCE_CLASS",
    96	    }
    97	)
    98	_CORE_SIGNATURES = {
    99	    "ComponentPaths": (
   100	        "(evidence_root_id: 'str', evidence_root: 'Path', report_path: 'Path', "
   101	        "spec_path: 'Path', order_manifest_path: 'Path', "
   102	        "calibration_cell_id: 'str', expected_kind: 'str') -> None"
   103	    ),
   104	    "pre_registration_gate": (
   105	        "(*, plan: 'Mapping[str, Any]', plan_sha256: 'str', "
   106	        "absolute: 'AuthenticatedComponent', "
   107	        "comparative: 'AuthenticatedComponent') -> 'None'"
   108	    ),
   109	    "mint_authenticated_artifact": (
   110	        "(*, artifact_id: 'str', plan: 'Mapping[str, Any]', "
   111	        "plan_sha256: 'str', calibration_plan_relative_path: 'str', "
   112	        "absolute: 'AuthenticatedComponent', "
   113	        "comparative: 'AuthenticatedComponent', project_commit: 'str', "
   114	        "project_tree_state: 'str') -> 'dict[str, Any]'"
   115	    ),
   116	    "validate_floor_artifact": (
   117	        "(value: 'Mapping', *, pinset_path: 'Path | None' = None, "
   118	        "expected_pinset_sha256: 'str | None' = None) -> 'list'"
   119	    ),
   120	    "mint_floor_artifact": (
   121	        "(*, artifact_id: 'str', floor_path: 'Path', statement_path: 'Path', "
   122	        "calibration_plan_path: 'Path', "
   123	        "calibration_plan_relative_path: 'str', "
   124	        "absolute_paths: 'ComponentPaths', comparative_paths: 'ComponentPaths', "
   125	        "project_commit: 'str', project_tree_state: 'str', "
   126	        "strict_validator: 'StrictValidator', "
   127	        "consumption_semantics_id: 'str | None' = None, "
   128	        "calibration_ledger_snapshot: 'CalibrationLedgerSnapshot | None' = None) "
   129	        "-> 'Mapping[str, Any]'"
   130	    ),
   131	}
   132	# D-109 R1.4 added the immutable ledger-snapshot parameter. Any future
   133	# change requires explicit signature-pin review plus parity evidence.
   134	StrictValidator = Callable[[Path, bool], Sequence[str]]
   135	
   136	
   137	class MintError(ValueError):
   138	    """A pinset or delegated mint gate failed; no artifact may be written."""
   139	
   140	
   141	@dataclass(frozen=True)
   142	class PlanPins:
   143	    plan_id: str
   144	    sha256: str
   145	    declared_calibration_scope: str
   146	    artifact_calibration_scope: str
   147	
   148	
   149	@dataclass(frozen=True)
   150	class ArtifactPins:
   151	    cell_id: str
   152	    transport_group_id: str
   153	    source_class: str
   154	
   155	
   156	@dataclass(frozen=True)
   157	class CellPins:
   158	    condition_family_id: str
   159	    condition_family_sha256: str
   160	    metric: str
   161	    window_class: str
   162	    target_precheck_path: tuple[str, ...]
   163	    operative_floor_six_decimal: str
   164	
   165	
   166	@dataclass(frozen=True)
   167	class ComponentPins:
   168	    evidence_root_id: str
   169	    calibration_cell_id: str
   170	    evaluation_basis_sha256: str
   171	    evaluation_basis_members: int
   172	    extraction_spec_members: int
   173	    expected_n: int
   174	    drift_allowance_j: float
   175	    order_manifest_id: str
   176	    consumption_semantics_id: str | None = None
   177	
   178	
   179	@dataclass(frozen=True)
   180	class MintPinset:
   181	    mint_tool_version: str
   182	    plan: PlanPins
   183	    artifact: ArtifactPins
   184	    cell: CellPins
   185	    absolute: ComponentPins
   186	    comparative: ComponentPins
   187	
   188	
   189	@dataclass(frozen=True)
   190	class V2Pinset:
   191	    """A closed final-stage v2 pinset.
   192	
   193	    ``value`` retains the authenticated JSON shape so producer and aggregate
   194	    hashes can be checked over the exact governed projections.  Desk-stage
   195	    requirements use a disjoint schema version and are never represented by
   196	    this type.
   197	    """
   198	
   199	    value: Mapping[str, Any]
   200	
   201	
   202	@dataclass(frozen=True)
   203	class ComponentInputs:
   204	    evidence_root: Path
   205	    report_path: Path
   206	    spec_path: Path
   207	    order_manifest_path: Path
   208	
   209	
   210	@dataclass(frozen=True)
   211	class V2CellComponents:
   212	    absolute: Any
   213	    comparative: Any
   214	    allowed_consumer_condition_families: tuple[Mapping[str, Any], ...]
   215	
   216	
   217	@dataclass(frozen=True)
   218	class V2ProducerInputs:
   219	    plan: Mapping[str, Any]
   220	    cells: Mapping[str, V2CellComponents]
   221	    evidence_root: Path
   222	    plan_sha256: str
   223	    plan_declared_sha256: str
   224	    plan_sidecar_sha256: str
   225	    calibration_acceptance: Mapping[str, Any]
   226	    calibration_acceptance_sha256: str
   227	    bracket_binding: Mapping[str, Any]
   228	    bracket_binding_sha256: str
   229	
   230	
   231	def _object(
   232	    value: object,
   233	    label: str,
   234	    expected_keys: set[str],
   235	) -> Mapping[str, Any]:
   236	    if not isinstance(value, Mapping):
   237	        raise MintError(f"{label} must be an object")
   238	    keys = set(value)
   239	    missing = sorted(expected_keys - keys)
   240	    extra = sorted(keys - expected_keys)
   241	    if missing or extra:
   242	        details = []
   243	        if missing:
   244	            details.append(f"missing={missing}")
   245	        if extra:
   246	            details.append(f"extra={extra}")
   247	        raise MintError(f"{label} schema mismatch: {'; '.join(details)}")
   248	    return value
   249	
   250	
   251	def _string(value: object, label: str) -> str:
   252	    if not isinstance(value, str) or not value or value != value.strip():
   253	        raise MintError(f"{label} must be a nonempty trimmed string")
   254	    return value
   255	
   256	
   257	def _evidence_root_id(value: object, label: str) -> str:
   258	    text = _string(value, label)
   259	    if _EVIDENCE_ROOT_ID_RE.fullmatch(text) is None:
   260	        raise MintError(
   261	            f"{label} must be a portable identifier containing only letters, "
   262	            "digits, dot, underscore, or hyphen"
   263	        )
   264	    return text
   265	
   266	
   267	def _sha256(value: object, label: str) -> str:
   268	    text = _string(value, label)
   269	    if _SHA256_RE.fullmatch(text) is None:
   270	        raise MintError(f"{label} must be 64 lowercase hexadecimal characters")
   271	    return text
   272	
   273	
   274	def _positive_int(value: object, label: str) -> int:
   275	    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
   276	        raise MintError(f"{label} must be a positive integer")
   277	    return value
   278	
   279	
   280	def _nonnegative_number(value: object, label: str) -> float:
  1690	def _mapping_attribute(value: object, name: str) -> object:
  1691	    if isinstance(value, Mapping):
  1692	        return value.get(name)
  1693	    return getattr(value, name, None)
  1694	
  1695	
  1696	def _require_postcollection_evidence_equal(
  1697	    field: str,
  1698	    pinned: object,
  1699	    evidenced: object,
  1700	    *,
  1701	    source: str,
  1702	) -> None:
  1703	    if pinned != evidenced:
  1704	        raise MintError(
  1705	            f"postcollection_evidence_mismatch: {field} mismatch against {source}"
  1706	        )
  1707	
  1708	
  1709	def _v2_extraction_postcollection_record(
  1710	    component: Any,
  1711	    cell_id: str,
  1712	    *,
  1713	    label: str,
  1714	) -> Mapping[str, Any]:
  1715	    block = component.report.get("floor_mint_postcollection")
  1716	    if not isinstance(block, Mapping) or set(block) != {
  1717	        "schema_version",
  1718	        "cells",
  1719	    }:
  1720	        raise MintError(
  1721	            f"postcollection_evidence_mismatch: {label} extraction report "
  1722	            "has no closed floor_mint_postcollection record"
  1723	        )
  1724	    if block.get("schema_version") != V2_EXTRACTION_POSTCOLLECTION_SCHEMA:
  1725	        raise MintError(
  1726	            f"postcollection_evidence_mismatch: {label} extraction report "
  1727	            "postcollection schema mismatch"
  1728	        )
  1729	    cells = block.get("cells")
  1730	    matches = (
  1731	        [row for row in cells if isinstance(row, Mapping) and row.get("cell_id") == cell_id]
  1732	        if isinstance(cells, list)
  1733	        else []
  1734	    )
  1735	    if len(matches) != 1:
  1736	        raise MintError(
  1737	            f"postcollection_evidence_mismatch: {label} extraction report "
  1738	            f"must contain exactly one {cell_id!r} record"
  1739	        )
  1740	    row = _object(
  1741	        matches[0],
  1742	        f"{label}.floor_mint_postcollection[{cell_id}]",
  1743	        {
  1744	            "cell_id",
  1745	            "observed_drift_s",
  1746	            "applied_allowance_s",
  1747	            "absolute_floor_full_precision",
  1748	            "comparative_floor_full_precision",
  1749	            "operative_floor_full_precision",
  1750	            "absolute_floor_six_decimal",
  1751	            "comparative_floor_six_decimal",
  1752	            "operative_floor_six_decimal",
  1753	        },
  1754	    )
  1755	    _string(row["cell_id"], f"{label}.cell_id")
  1756	    _decimal_text(row["observed_drift_s"], f"{label}.observed_drift_s")
  1757	    _decimal_text(row["applied_allowance_s"], f"{label}.applied_allowance_s")
  1758	    for name in (
  1759	        "absolute_floor_full_precision",
  1760	        "comparative_floor_full_precision",
  1761	        "operative_floor_full_precision",
  1762	    ):
  1763	        _decimal_text(row[name], f"{label}.{name}")
  1764	    for name in (
  1765	        "absolute_floor_six_decimal",
  1766	        "comparative_floor_six_decimal",
  1767	        "operative_floor_six_decimal",
  1768	    ):
  1769	        _six_decimal(row[name], f"{label}.{name}")
  1770	    for component_name in ("absolute", "comparative", "operative"):
  1771	        _verify_six_decimal_rendering(
  1772	            row[f"{component_name}_floor_full_precision"],
  1773	            row[f"{component_name}_floor_six_decimal"],
  1774	            label=f"{label}.{component_name}_floor",
  1775	        )
  1776	    return row
  1777	
  1778	
  1779	def _v2_authenticate_bracket_binding(
  1780	    *,
  1781	    producer: Mapping[str, Any],
  1782	    inputs: V2ProducerInputs,
  1783	    ledger_snapshot: Any,
  1784	) -> tuple[Any, Any]:
  1785	    label = f"producer {producer['plan']['plan_id']!r}"
  1786	    binding = inputs.bracket_binding
  1787	    if not isinstance(binding, Mapping) or set(binding) != {
  1788	        "schema_version",
  1789	        "ledger_schema",
  1790	        "session_id",
  1791	        "window_id",
  1792	        "plan_id",
  1793	        "plan_sha256",
  1794	        "evidence_root_id",
  1795	        "runs_root",
  1796	        "capability_receipt_digest",
  1797	        "terminal_head",
  1798	        "endpoints",
  1799	        "binding_digest",
  1800	    }:
  1801	        raise MintError(
  1802	            f"postcollection_evidence_mismatch: {label} bracket binding schema mismatch"
  1803	        )
  1804	    if binding.get("schema_version") != V2_BRACKET_BINDING_SCHEMA:
  1805	        raise MintError(
  1806	            f"postcollection_evidence_mismatch: {label} bracket binding version mismatch"
  1807	        )
  1808	    if binding.get("ledger_schema") != "joulewise.calibration_observation_ledger.v1":
  1809	        raise MintError(
  1810	            f"postcollection_evidence_mismatch: {label} bracket ledger schema mismatch"
  1811	        )
  1812	    observed_binding_digest = _canonical_json_sha256(
  1813	        {key: value for key, value in binding.items() if key != "binding_digest"}
  1814	    )
  1815	    if binding.get("binding_digest") != observed_binding_digest:
  1816	        raise MintError(
  1817	            f"postcollection_evidence_mismatch: {label} binding digest mismatch"
  1818	        )
  1819	    for field, expected in (
  1820	        ("plan_id", producer["plan"]["plan_id"]),
  1821	        ("plan_sha256", producer["plan"]["sha256"]),
  1822	        ("evidence_root_id", producer["evidence_root_id"]),
  1823	        ("runs_root", str(inputs.evidence_root.resolve(strict=False))),
  1824	    ):
  1825	        if binding.get(field) != expected:
  1826	            raise MintError(
  1827	            f"postcollection_evidence_mismatch: {label} binding {field} mismatch"
  1828	        )
  1829	    for field in ("session_id", "window_id"):
  1830	        if not isinstance(binding.get(field), str) or not binding[field]:
  1831	            raise MintError(
  1832	                f"postcollection_evidence_mismatch: {label} binding {field} mismatch"
  1833	            )
  1834	    _sha256(
  1835	        binding.get("capability_receipt_digest"),
  1836	        f"{label}.capability_receipt_digest",
  1837	    )
  1838	    _sha256(
  1839	        inputs.bracket_binding_sha256,
  1840	        f"{label}.bracket_binding_sha256",
  1841	    )
  1842	    if not bool(_mapping_attribute(ledger_snapshot, "valid")):
  1843	        raise MintError(
  1844	            f"postcollection_evidence_mismatch: {label} ledger snapshot is invalid"
  1845	        )
  1846	    if _mapping_attribute(ledger_snapshot, "ledger_schema") != binding[
  1847	        "ledger_schema"
  1848	    ]:
  1849	        raise MintError(
  1850	            f"postcollection_evidence_mismatch: {label} ledger snapshot schema mismatch"
  1851	        )
  1852	    receipts = _mapping_attribute(ledger_snapshot, "receipts")
  1853	    observations = _mapping_attribute(ledger_snapshot, "observations")
  1854	    sessions = _mapping_attribute(ledger_snapshot, "bracket_session_by_id")
  1855	    if not isinstance(receipts, tuple | list) or not isinstance(
  1856	        observations, tuple | list
  1857	    ):
  1858	        raise MintError(
  1859	            f"postcollection_evidence_mismatch: {label} ledger snapshot is incomplete"
  1860	        )
  1861	    session = (
  1862	        sessions.get(binding["session_id"])
  1863	        if isinstance(sessions, Mapping)
  1864	        else None
  1865	    )
  1866	    if session is None:
  1867	        raise MintError(
  1868	            f"postcollection_evidence_mismatch: {label} bracket session is absent"
  1869	        )
  1870	    for field, expected in (
  1871	        ("state", "finalized"),
  1872	        ("window_id", binding["window_id"]),
  1873	        ("plan_id", binding["plan_id"]),
  1874	        ("plan_sha256", binding["plan_sha256"]),
  1875	        ("evidence_root_id", binding["evidence_root_id"]),
  1876	        ("runs_root", binding["runs_root"]),
  1877	        (
  1878	            "capability_receipt_digest",
  1879	            binding["capability_receipt_digest"],
  1880	        ),
  1881	    ):
  1882	        if _mapping_attribute(session, field) != expected:
  1883	            raise MintError(
  1884	                f"postcollection_evidence_mismatch: {label} bracket session {field} mismatch"
  1885	            )
  1886	    finalized_slots = _mapping_attribute(session, "finalized_slots")
  1887	    if not isinstance(finalized_slots, Mapping) or set(finalized_slots) != {
  1888	        "pre",
  1889	        "post",
  1890	    }:
  1891	        raise MintError(
  1892	            f"postcollection_evidence_mismatch: {label} finalized bracket slots mismatch"
  1893	        )
  1894	    receipt_digests = {
  1895	        row.get("receipt_digest")
  1896	        for row in receipts
  1897	        if isinstance(row, Mapping) and _SHA256_RE.fullmatch(str(row.get("receipt_digest")))
  1898	    }
  1899	    if binding.get("capability_receipt_digest") not in receipt_digests:
  1900	        raise MintError(
  1901	            f"postcollection_evidence_mismatch: {label} capability receipt is absent"
  1902	        )
  1903	    endpoints = binding.get("endpoints")
  1904	    if not isinstance(endpoints, Mapping) or set(endpoints) != {"pre", "post"}:
  1905	        raise MintError(
  1906	            f"postcollection_evidence_mismatch: {label} binding endpoints mismatch"
  1907	        )
  1908	    resolved = []
  1909	    for role in ("pre", "post"):
  1910	        endpoint = endpoints.get(role)
  1911	        if not isinstance(endpoint, Mapping) or set(endpoint) != {
  1912	            "attempt_id",
  1913	            "receipt_digest",
  1914	            "content_digest",
  1915	        }:
  1916	            raise MintError(
  1917	                f"postcollection_evidence_mismatch: {label} {role} endpoint schema mismatch"
  1918	            )
  1919	        _sha256(endpoint.get("receipt_digest"), f"{label}.{role}.receipt_digest")
  1920	        _sha256(endpoint.get("content_digest"), f"{label}.{role}.content_digest")
  1921	        matches = [
  1922	            observation
  1923	            for observation in observations
  1924	            if _mapping_attribute(observation, "attempt_id")
  1925	            == endpoint.get("attempt_id")
  1926	            and _mapping_attribute(observation, "receipt_digest")
  1927	            == endpoint.get("receipt_digest")
  1928	            and _mapping_attribute(observation, "content_id")
  1929	            == endpoint.get("content_digest")
  1930	        ]
  1931	        if len(matches) != 1:
  1932	            raise MintError(
  1933	                f"postcollection_evidence_mismatch: {label} {role} receipt/content mismatch"
  1934	            )
  1935	        observation = matches[0]
  1936	        finalized_observation = finalized_slots.get(role)
  1937	        if any(
  1938	            _mapping_attribute(finalized_observation, field)
  1939	            != _mapping_attribute(observation, field)
  1940	            for field in (
  1941	                "sequence",
  1942	                "attempt_id",
  1943	                "receipt_digest",
  1944	                "content_id",
  1945	            )
  1946	        ):
  1947	            raise MintError(
  1948	                f"postcollection_evidence_mismatch: {label} {role} finalized slot mismatch"
  1949	            )
  1950	        for field, expected in (
  1951	            ("disposition", "valid"),
  1952	            ("bracket_session_id", binding.get("session_id")),
  1953	            ("bracket_slot", role),
  1954	            ("bracket_window_id", binding.get("window_id")),
  1955	            ("bracket_plan_id", producer["plan"]["plan_id"]),
  1956	            ("bracket_plan_sha256", producer["plan"]["sha256"]),
  1957	            ("bracket_evidence_root_id", producer["evidence_root_id"]),
  1958	        ):
  1959	            if _mapping_attribute(observation, field) != expected:
  1960	                raise MintError(
  1961	                    f"postcollection_evidence_mismatch: {label} {role} {field} mismatch"
  1962	                )
  1963	        resolved.append(observation)
  1964	    terminal = binding.get("terminal_head")
  1965	    post_sequence = _mapping_attribute(resolved[1], "sequence")
  1966	    post_receipt = _mapping_attribute(resolved[1], "receipt_digest")
  1967	    if (
  1968	        not isinstance(terminal, Mapping)
  1969	        or set(terminal) != {"sequence", "head_digest", "ledger_schema"}
  1970	        or terminal.get("ledger_schema")
  1971	        != "joulewise.calibration_observation_ledger.v1"
  1972	        or isinstance(terminal.get("sequence"), bool)
  1973	        or terminal.get("sequence") != post_sequence
  1974	        or terminal.get("head_digest") != post_receipt
  1975	        or not isinstance(post_sequence, int)
  1976	        or post_sequence < 1
  1977	        or post_sequence > len(receipts)
  1978	        or not isinstance(receipts[post_sequence - 1], Mapping)
  1979	        or receipts[post_sequence - 1].get("receipt_digest") != post_receipt
  1980	    ):
  1981	        raise MintError(
  1982	            f"postcollection_evidence_mismatch: {label} terminal ledger head mismatch"
  1983	        )
  1984	    return resolved[0], resolved[1]
  1985	
  1986	
  1987	def _v2_gate_producer_inventory(
  1988	    producer: Mapping[str, Any],
  1989	    inputs: V2ProducerInputs,
  1990	) -> None:
  1991	    plan = producer["plan"]
  1992	    plan_id = plan["plan_id"]
  1993	    if inputs.plan_sha256 != plan["sha256"]:
  1994	        raise MintError(f"producer {plan_id!r}: calibration plan sha256 mismatch")
  1995	    if inputs.plan_declared_sha256 != plan["declared_sha256"]:
  1996	        raise MintError(f"producer {plan_id!r}: declared plan sha256 mismatch")
  1997	    if inputs.plan_sidecar_sha256 != plan["sidecar_sha256"]:
  1998	        raise MintError(f"producer {plan_id!r}: plan sidecar sha256 mismatch")
  1999	    if inputs.plan.get("plan_id") != plan_id or inputs.plan.get(
  2000	        "calibration_scope"
  2001	    ) != plan["declared_calibration_scope"]:
  2002	        raise MintError(f"producer {plan_id!r}: calibration plan identity mismatch")
  2003	    acceptance = inputs.calibration_acceptance
  2004	    acceptance_pins = producer["calibration_acceptance"]
  2005	    if (
  2006	        not isinstance(acceptance, Mapping)
  2007	        or acceptance.get("acceptance_id") != acceptance_pins["acceptance_id"]
  2008	        or inputs.calibration_acceptance_sha256
  2009	        != acceptance_pins["artifact_sha256"]
  2010	        or acceptance.get("derivation_sha256")
  2011	        != acceptance_pins["derivation_sha256"]
  2012	        or acceptance.get("schema_version")
  2013	        != acceptance_pins["derivation_rule_id"]
  2014	    ):
  2015	        raise MintError(
  2016	            f"producer {plan_id!r}: calibration acceptance evidence mismatch"
  2017	        )
  2018	    components = [
  2019	        component
  2020	        for cell in inputs.cells.values()
  2021	        for component in (cell.absolute, cell.comparative)
  2022	    ]
  2023	    if not components:
  2024	        raise MintError(f"producer {plan_id!r}: no authenticated components")
  2025	    extraction_sha256s = {component.spec_sha256 for component in components}
  2026	    if extraction_sha256s != {producer["extraction_spec"]["sha256"]}:
  2027	        raise MintError(f"producer {plan_id!r}: extraction spec inventory mismatch")
  2028	    unique_members = {
  2029	        member.bundle_id for component in components for member in component.members
  2030	    }
  2031	    if len(unique_members) != producer["extraction_spec"]["member_count"]:
  2032	        raise MintError(f"producer {plan_id!r}: extraction member inventory mismatch")
  2033	    model_hashes = {
  2034	        component.source_regime.get("stack_identity", {}).get(
  2035	            "model_artifact_sha256"
  2036	        )
  2037	        for component in components
  2038	    }
  2039	    runtime_hashes = {
  2040	        component.source_regime.get("stack_identity_sha256")
  2041	        for component in components
  2042	    }
  2043	    config_hashes = {
  2044	        component.scientific_config_identity_sha256 for component in components
  2045	    }
  2046	    runtime_pins = producer["model_runtime_config"]
  2047	    if model_hashes != {runtime_pins["model_artifact_sha256"]}:
  2048	        raise MintError(f"producer {plan_id!r}: model artifact inventory mismatch")
  2049	    if runtime_hashes != {runtime_pins["runtime_identity_sha256"]}:
  2050	        raise MintError(f"producer {plan_id!r}: runtime identity inventory mismatch")
  2051	    if config_hashes != {runtime_pins["config_set_sha256"]}:
  2052	        raise MintError(f"producer {plan_id!r}: config-set inventory mismatch")
  2053	
  2054	
  2055	def _v2_gate_postcollection(
  2056	    *,
  2057	    producer: Mapping[str, Any],
  2058	    cell_pins: Mapping[str, Any],
  2059	    cell_inputs: V2CellComponents,
  2060	    producer_inputs: V2ProducerInputs,
  2061	    ledger_snapshot: Any,
  2062	) -> None:
  2063	    post = cell_pins["postcollection"]
  2064	    pre, post_observation = _v2_authenticate_bracket_binding(
  2065	        producer=producer,
  2066	        inputs=producer_inputs,
  2067	        ledger_snapshot=ledger_snapshot,
  2068	    )
  2069	    expected_binding_sha256 = post["bracket_binding_sha256"]
  2070	    _require_postcollection_evidence_equal(
  2071	        "bracket_binding_sha256",
  2072	        expected_binding_sha256,
  2073	        producer_inputs.bracket_binding_sha256,
  2074	        source="supplied bracket-binding artifact bytes",
  2075	    )
  2076	    binding = producer_inputs.bracket_binding
  2077	    endpoint_fields = {
  2078	        "pre": ("pre_receipt_sha256", "pre_content_sha256"),
  2079	        "post": ("post_receipt_sha256", "post_content_sha256"),
  2080	    }
  2081	    for role, observation in (("pre", pre), ("post", post_observation)):
  2082	        receipt_field, content_field = endpoint_fields[role]
  2083	        _require_postcollection_evidence_equal(
  2084	            receipt_field,
  2085	            post[receipt_field],
  2086	            _mapping_attribute(observation, "receipt_digest"),
  2087	            source=f"authenticated ledger {role} observation",
  2088	        )
  2089	        _require_postcollection_evidence_equal(
  2090	            content_field,
  2091	            post[content_field],
  2092	            _mapping_attribute(observation, "content_id"),
  2093	            source=f"authenticated ledger {role} observation",
  2094	        )
  2095	    _require_postcollection_evidence_equal(
  2090	            content_field,
  2091	            post[content_field],
  2092	            _mapping_attribute(observation, "content_id"),
  2093	            source=f"authenticated ledger {role} observation",
  2094	        )
  2095	    _require_postcollection_evidence_equal(
  2096	        "terminal_ledger_head_sha256",
  2097	        post["terminal_ledger_head_sha256"],
  2098	        binding["terminal_head"]["head_digest"],
  2099	        source="authenticated bracket-binding terminal head",
  2100	    )
  2101	    try:
  2102	        observed_drift = abs(
  2103	            _decimal_text(
  2104	                _mapping_attribute(pre, "exact_bound_lexeme_s"),
  2105	                "ledger pre exact_bound_lexeme_s",
  2106	            )
  2107	            - _decimal_text(
  2108	                _mapping_attribute(post_observation, "exact_bound_lexeme_s"),
  2109	                "ledger post exact_bound_lexeme_s",
  2110	            )
  2111	        )
  2112	    except (InvalidOperation, MintError) as exc:
  2113	        raise MintError(
  2114	            "postcollection_evidence_mismatch: ledger endpoint drift is not exact Decimal evidence"
  2115	        ) from exc
  2116	    _require_postcollection_evidence_equal(
  2117	        "observed_drift_s",
  2118	        _decimal_text(post["observed_drift_s"], "postcollection.observed_drift_s"),
  2119	        observed_drift,
  2120	        source="authenticated ledger endpoint bounds",
  2121	    )
  2122	    actual_components = (cell_inputs.absolute, cell_inputs.comparative)
  2123	    for component in actual_components:
  2124	        _require_postcollection_evidence_equal(
  2125	            "extraction_report_sha256",
  2126	            post["extraction_report_sha256"],
  2127	            component.report_sha256,
  2128	            source=f"supplied {component.kind} extraction-report artifact bytes",
  2129	        )
  2130	    records = [
  2131	        _v2_extraction_postcollection_record(
  2132	            component,
  2133	            cell_pins["cell_id"],
  2134	            label=f"{cell_pins['cell_id']}.{component.kind}",
  2135	        )
  2136	        for component in actual_components
  2137	    ]
  2138	    if records[0] != records[1]:
  2139	        raise MintError(
  2140	            "postcollection_evidence_mismatch: component extraction reports disagree"
  2141	        )
  2142	    report_record = records[0]
  2143	    for name in (
  2144	        "observed_drift_s",
  2145	        "applied_allowance_s",
  2146	        "absolute_floor_full_precision",
  2147	        "comparative_floor_full_precision",
  2148	        "operative_floor_full_precision",
  2149	        "absolute_floor_six_decimal",
  2150	        "comparative_floor_six_decimal",
  2151	        "operative_floor_six_decimal",
  2152	    ):
  2153	        _require_postcollection_evidence_equal(
  2154	            name,
  2155	            post[name],
  2156	            report_record[name],
  2157	            source="authenticated extraction-report record",
  2158	        )
  2159	    actual_values = (
  2160	        cell_inputs.absolute.cell.get("floor", {}).get(
  2161	            "drift_widened_guarded_floor_j"
  2162	        ),
  2163	        cell_inputs.comparative.cell.get("floor", {}).get(
  2164	            "drift_widened_guarded_floor_j"
  2165	        ),
  2166	    )
  2167	    expected_values = (
  2168	        _decimal_text(
  2169	            post["absolute_floor_full_precision"],
  2170	            "postcollection.absolute_floor_full_precision",
  2171	        ),
  2172	        _decimal_text(
  2173	            post["comparative_floor_full_precision"],
  2174	            "postcollection.comparative_floor_full_precision",
  2175	        ),
  2176	    )
  2177	    for name, actual, expected in zip(
  2178	        ("absolute", "comparative"), actual_values, expected_values
  2179	    ):
  2180	        if isinstance(actual, bool) or not isinstance(actual, int | float):
  2181	            raise MintError(
  2182	                f"postcollection_evidence_mismatch: {name} extraction value is not numeric"
  2183	            )
  2184	        if Decimal(str(actual)) != expected:
  2185	            raise MintError(
  2186	                f"postcollection_evidence_mismatch: {name} full-precision value mismatch"
  2187	            )
  2188	
  2189	
  2190	def _v2_allowed_families(
  2191	    supplied: Sequence[Mapping[str, Any]],
  2192	    pins: Sequence[Mapping[str, Any]],
  2193	    *,
  2194	    label: str,
  2195	) -> list[Mapping[str, Any]]:
  2196	    expected = [
  2197	        (row["condition_family_id"], row["condition_family_sha256"])
  2198	        for row in pins
  2199	    ]
  2200	    observed = []
  2201	    normalized = []
  2202	    from joulewise.detection_floor import (
  2203	        CONDITION_FAMILY_DOMAIN,
  2204	        canonical_domain_sha256,
  2205	    )
  2206	
  2207	    for index, row in enumerate(supplied):
  2208	        if not isinstance(row, Mapping):
  2209	            raise MintError(f"{label}[{index}] must be an object")
  2210	        definition = row.get("condition_family_definition")
  2211	        family_id = row.get("condition_family_id")
  2212	        family_sha256 = row.get("condition_family_sha256")
  2213	        if not isinstance(definition, Mapping) or not isinstance(family_id, str):
  2214	            raise MintError(f"{label}[{index}] is incomplete")
  2215	        if canonical_domain_sha256(CONDITION_FAMILY_DOMAIN, definition) != (
  2216	            family_sha256
  2217	        ):
  2218	            raise MintError(f"{label}[{index}] condition-family hash mismatch")
  2219	        observed.append((family_id, family_sha256))
  2220	        normalized.append(dict(row))
  2221	    if observed != expected:
  2222	        raise MintError(f"{label} does not match the transport allowlist pins")
  2223	    return normalized
  2224	
  2225	
  2226	def _v2_pre_registration_gate(
  2227	    *,
  2228	    core: ModuleType,
  2229	    producer: Mapping[str, Any],
  2230	    cell_pins: Mapping[str, Any],
  2231	    plan: Mapping[str, Any],
  2232	    absolute: Any,
  2233	    comparative: Any,
  2234	) -> Mapping[str, Any]:
  2235	    plan_pins = producer["plan"]
  2236	    if absolute.order_manifest.get("calibration_plan_sha256") != plan_pins[
  2237	        "sha256"
  2238	    ] or comparative.order_manifest.get("calibration_plan_sha256") != plan_pins[
  2239	        "sha256"
  2240	    ]:
  2241	        raise MintError("v2 pre-registration gate: order-manifest plan sha mismatch")
  2242	    if absolute.order_manifest.get("plan_id") != plan.get(
  2243	        "plan_id"
  2244	    ) or comparative.order_manifest.get("plan_id") != plan.get("plan_id"):
  2245	        raise MintError("v2 pre-registration gate: order-manifest plan id mismatch")
  2246	    absolute_binding = core._definition_binding(absolute)
  2247	    comparative_bindings = comparative.spec_cell.get(
  2248	        "condition_family_definitions"
  2249	    )
  2250	    if (
  2251	        not isinstance(comparative_bindings, Mapping)
  2252	        or comparative_bindings.get("A") != comparative_bindings.get("B")
  2253	        or absolute_binding != comparative_bindings.get("A")
  2254	        or absolute_binding.get("condition_family_id")
  2255	        != cell_pins["condition_family_id"]
  2256	        or absolute_binding.get("condition_family_sha256")
  2257	        != cell_pins["condition_family_sha256"]
  2258	        or absolute_binding.get("condition_family_definition", {}).get(
  2259	            "abba_alias_relation"
  2260	        )
  2261	        != "A_equals_B"
  2262	    ):
  2263	        raise MintError(
  2264	            "v2 pre-registration gate: components are not the pinned A==B null"
  2265	        )
  2266	    if not core._diagnostics_are_nonpublishing(
  2267	        absolute.report
  2268	    ) or not core._diagnostics_are_nonpublishing(comparative.report):
  2269	        raise MintError(
  2270	            "v2 pre-registration gate: diagnostic floor is marked as published"
  2271	        )
  2272	    if absolute.scientific_config_identity_sha256 != (
  2273	        comparative.scientific_config_identity_sha256
  2274	    ):
  2275	        raise MintError(
  2730	            producer_cell_ids = [cell["cell_id"] for cell in producer["cells"]]
  2731	            producer_group_ids = [
  2732	                cell["transport_group_id"] for cell in producer["cells"]
  2733	            ]
  2734	            component = copy.deepcopy(dict(artifact))
  2735	            component["artifact_id"] = component_pin["artifact_id"]
  2736	            component["provenance"] = {
  2737	                "calibration_plan": expected_producer_plans[
  2738	                    value["producer_plans"].index(producer)
  2739	                ],
  2740	                "mint_tool_version": V2_MINT_TOOL_VERSION,
  2741	                "implementation": copy.deepcopy(
  2742	                    provenance.get("implementation")
  2743	                ),
  2744	            }
  2745	            component["cells"] = [
  2746	                copy.deepcopy(cell_by_id[cell_id])
  2747	                for cell_id in producer_cell_ids
  2748	                if cell_id in cell_by_id
  2749	            ]
  2750	            component["transport_groups"] = [
  2751	                copy.deepcopy(group_by_id[group_id])
  2752	                for group_id in producer_group_ids
  2753	                if group_id in group_by_id
  2754	            ]
  2755	            if len(component["cells"]) != 2 or len(
  2756	                component["transport_groups"]
  2757	            ) != 2:
  2758	                continue
  2759	            observed_component_sha256 = _artifact_sha256(component)
  2760	            if observed_component_sha256 != component_pin["sha256"]:
  2761	                errors.append(
  2762	                    "artifact: component artifact hash mismatch for "
  2763	                    f"{component_pin['plan_id']!r}"
  2764	                )
  2765	    return errors
  2766	
  2767	
  2768	def mint_multi_cell_authenticated_artifact(
  2769	    *,
  2770	    pinset_path: Path,
  2771	    pinset_sha256: str,
  2772	    producer_inputs: Mapping[str, V2ProducerInputs],
  2773	    calibration_ledger_snapshot: Any,
  2774	    project_commit: str,
  2775	    project_tree_state: str,
  2776	) -> Mapping[str, Any]:
  2777	    """Mint the D-117 two-plan/four-cell artifact from authenticated inputs."""
  2778	
  2779	    loaded = load_pinset(pinset_path, pinset_sha256)
  2780	    if not isinstance(loaded, V2Pinset):
  2781	        raise MintError("multi-cell mint requires a final v2 pinset")
  2782	    _validate_v2_pin_hashes(loaded)
  2783	    artifact, components = _build_v2_artifacts(
  2784	        pinset=loaded,
  2785	        pinset_path=pinset_path,
  2786	        pinset_sha256=pinset_sha256,
  2787	        producer_inputs=producer_inputs,
  2788	        calibration_ledger_snapshot=calibration_ledger_snapshot,
  2789	        project_commit=project_commit,
  2790	        project_tree_state=project_tree_state,
  2791	    )
  2792	    for index, (component, expected) in enumerate(
  2793	        zip(components, loaded.value["aggregate"]["component_artifacts"])
  2794	    ):
  2795	        observed = _artifact_sha256(component)
  2796	        if observed != expected["sha256"]:
  2797	            raise MintError(
  2798	                "aggregate/component hash mismatch: component artifact "
  2799	                f"{index} expected {expected['sha256']}, observed {observed}"
  2800	            )
  2801	    errors = validate_floor_artifact(
  2802	        artifact=artifact,
  2803	        pinset_path=pinset_path,
  2804	        pinset_sha256=pinset_sha256,
  2805	    )
  2806	    if errors:
  2807	        raise MintError(f"constructed v2 artifact is invalid: {errors[0]}")
  2808	    return artifact
  2809	
  2810	
  2811	def _load_v2_input_manifest(path: Path) -> Mapping[str, Any]:
  2812	    try:
  2813	        raw = Path(path).read_bytes()
  2814	    except OSError as exc:
  2815	        raise MintError(
  2816	            f"v2 input manifest cannot be read: {exc.strerror or type(exc).__name__}"
  2817	        ) from exc
  2818	    try:
  2819	        value = json.loads(
  2820	            raw.decode("utf-8"),
  2821	            object_pairs_hook=_reject_duplicate_keys,
  2822	            parse_constant=_reject_nonfinite_json,
  2823	        )
  2824	    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
  2825	        raise MintError(f"v2 input manifest is not valid UTF-8 JSON: {exc}") from exc
  2826	    root = _object(
  2827	        value,
  2828	        "v2 input manifest",
  2829	        {
  2830	            "schema_version",
  2831	            "calibration_acceptance",
  2832	            "calibration_ledger",
  2833	            "calibration_ledger_head_pin",
  2834	            "producer_plans",
  2835	        },
  2836	    )
  2837	    if root["schema_version"] != "joulewise.floor_mint_inputs.v2":
  2838	        raise MintError(
  2839	            "v2 input manifest.schema_version must equal "
  2840	            "'joulewise.floor_mint_inputs.v2'"
  2841	        )
  2842	    if not isinstance(root["producer_plans"], list):
  2843	        raise MintError("v2 input manifest.producer_plans must be an array")
  2844	    return root
  2845	
  2846	
  2847	def _v2_component_input_paths(
  2848	    value: object,
  2849	    label: str,
  2850	) -> ComponentInputs:
  2851	    row = _object(
  2852	        value,
  2853	        label,
  2854	        {"evidence_root", "report", "spec", "order_manifest"},
  2855	    )
  2856	    return ComponentInputs(
  2857	        evidence_root=Path(_string(row["evidence_root"], f"{label}.evidence_root")),
  2858	        report_path=Path(_string(row["report"], f"{label}.report")),
  2859	        spec_path=Path(_string(row["spec"], f"{label}.spec")),
  2860	        order_manifest_path=Path(
  2861	            _string(row["order_manifest"], f"{label}.order_manifest")
  2862	        ),
  2863	    )
  2864	
  2865	
  2866	def _load_v2_ledger_snapshot(
  2867	    core: ModuleType,
  2868	    *,
  2869	    acceptance: Mapping[str, Any],
  2870	    ledger_path: Path,
  2871	    head_pin_path: Path,
  2872	) -> Any:
  2873	    cutoff = (
  2874	        acceptance.get("ledger_cutoff")
  2875	        if isinstance(acceptance, Mapping)
  2876	        else None
  2877	    )
  2878	    return core.load_calibration_ledger_snapshot(
  2879	        ledger_path=ledger_path,
  2880	        head_pin_path=head_pin_path,
  2881	        baseline_sequence=(
  2882	            cutoff.get("sequence") if isinstance(cutoff, Mapping) else None
  2883	        ),
  2884	        baseline_digest=(
  2885	            cutoff.get("head_digest") if isinstance(cutoff, Mapping) else None
  2886	        ),
  2887	    )
  2888	
  2889	
  2890	def _authenticate_v2_inputs(
  2891	    *,
  2892	    pinset: V2Pinset,
  2893	    pinset_path: Path,
  2894	    pinset_sha256: str,
  2895	    input_manifest_path: Path,
  2896	    strict_validator: StrictValidator,
  2897	    consumption_semantics_id: str | None,
  2898	) -> tuple[
  2899	    Mapping[str, V2ProducerInputs],
  2900	    Mapping[str, Path],
  2901	    Any,
  2902	]:
  2903	    manifest = _load_v2_input_manifest(input_manifest_path)
  2904	    rows = manifest["producer_plans"]
  2905	    if len(rows) != len(pinset.value["producer_plans"]):
  2906	        raise MintError("v2 input manifest must contain every producer plan exactly once")
  2907	    by_plan_id: dict[str, Mapping[str, Any]] = {}
  2908	    for index, row_value in enumerate(rows):
  2909	        label = f"v2 input manifest.producer_plans[{index}]"
  2910	        row = _object(
  2911	            row_value,
  2912	            label,
  2913	            {
  2914	                "plan_id",
  2915	                "calibration_plan",
  2916	                "calibration_plan_sidecar",
  2917	                "bracket_binding",
  2918	                "cells",
  2919	            },
  2920	        )
  2921	        plan_id = _string(row["plan_id"], f"{label}.plan_id")
  2922	        if plan_id in by_plan_id:
  2923	            raise MintError("v2 input manifest producer plan ids must be unique")
  2924	        by_plan_id[plan_id] = row
  2925	
  2926	    evidence_core = _fresh_original_core()
  2927	    acceptance_path = Path(
  2928	        _string(
  2929	            manifest["calibration_acceptance"],
  2930	            "v2 input manifest.calibration_acceptance",
  2931	        )
  2932	    )
  2933	    try:
  2934	        acceptance_raw = acceptance_path.read_bytes()
  2935	    except OSError as exc:
  2936	        raise MintError(
  2937	            "v2 calibration acceptance cannot be read: "
  2938	            f"{exc.strerror or type(exc).__name__}"
  2939	        ) from exc
  2940	    acceptance = evidence_core.load_calibration_acceptance_bound(acceptance_path)
  2941	    if not isinstance(acceptance, Mapping):
  2942	        raise MintError("v2 calibration acceptance evidence is not authenticated")
  2943	    try:
  2944	        acceptance_after = acceptance_path.read_bytes()
  2945	    except OSError as exc:
  2946	        raise MintError(
  2947	            "v2 calibration acceptance cannot be re-read after authentication: "
  2948	            f"{exc.strerror or type(exc).__name__}"
  2949	        ) from exc
  2950	    if acceptance_after != acceptance_raw:
  2951	        raise MintError("v2 calibration acceptance changed during authentication")
  2952	    acceptance_sha256 = hashlib.sha256(acceptance_raw).hexdigest()
  2953	    ledger_snapshot = _load_v2_ledger_snapshot(
  2954	        evidence_core,
  2955	        acceptance=acceptance,
  2956	        ledger_path=Path(
  2957	            _string(
  2958	                manifest["calibration_ledger"],
  2959	                "v2 input manifest.calibration_ledger",
  2960	            )
  2961	        ),
  2962	        head_pin_path=Path(
  2963	            _string(
  2964	                manifest["calibration_ledger_head_pin"],
  2965	                "v2 input manifest.calibration_ledger_head_pin",
  2966	            )
  2967	        ),
  2968	    )
  2969	    if not bool(getattr(ledger_snapshot, "valid", False)):
  2970	        raise MintError("v2 calibration ledger snapshot is not authenticated")
  2971	
  2972	    result: dict[str, V2ProducerInputs] = {}
  2973	    evidence_roots: dict[str, Path] = {}
  2974	    for producer_index, producer in enumerate(pinset.value["producer_plans"]):
  2975	        plan_id = producer["plan"]["plan_id"]
  2976	        manifest_row = by_plan_id.get(plan_id)
  2977	        if manifest_row is None:
  2978	            raise MintError(f"v2 input manifest is missing producer {plan_id!r}")
  2979	        plan_path = Path(
  2980	            _string(
  2981	                manifest_row["calibration_plan"],
  2982	                f"v2 input manifest producer {plan_id}.calibration_plan",
  2983	            )
  2984	        )
  2985	        try:
  2986	            plan_raw = plan_path.read_bytes()
  2987	            plan = json.loads(
  2988	                plan_raw.decode("utf-8"),
  2989	                object_pairs_hook=_reject_duplicate_keys,
  2990	                parse_constant=_reject_nonfinite_json,
  2991	            )
  2992	        except OSError as exc:
  2993	            raise MintError(
  2994	                f"producer {plan_id!r} calibration plan cannot be read: "
  2995	                f"{exc.strerror or type(exc).__name__}"
  2996	            ) from exc
  2997	        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
  2998	            raise MintError(
  2999	                f"producer {plan_id!r} calibration plan is invalid JSON: {exc}"
  3000	            ) from exc
  3001	        if not isinstance(plan, Mapping):
  3002	            raise MintError(f"producer {plan_id!r} calibration plan must be an object")
  3003	        if hashlib.sha256(plan_raw).hexdigest() != producer["plan"]["sha256"]:
  3004	            raise MintError(f"producer {plan_id!r} calibration plan sha256 mismatch")
  3005	        sidecar_path = Path(
  3006	            _string(
  3007	                manifest_row["calibration_plan_sidecar"],
  3008	                f"v2 input manifest producer {plan_id}.calibration_plan_sidecar",
  3009	            )
  3010	        )
  3011	        try:
  3012	            sidecar_raw = sidecar_path.read_bytes()
  3013	            sidecar_text = sidecar_raw.decode("utf-8")
  3014	        except OSError as exc:
  3015	            raise MintError(
  3016	                f"producer {plan_id!r} plan sidecar cannot be read: "
  3017	                f"{exc.strerror or type(exc).__name__}"
  3018	            ) from exc
  3019	        except UnicodeDecodeError as exc:
  3020	            raise MintError(

exec
/bin/zsh -lc "nl -ba scripts/mint_floor_artifact_generalized.py | sed -n '1890,2190p'; nl -ba scripts/mint_floor_artifact_generalized.py | sed -n '3000,3210p'; nl -ba scripts/mint_floor_artifact_generalized.py | sed -n '3210,3400p'; nl -ba scripts/mint_floor_artifact_generalized.py | sed -n '3400,3580p'" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u3
 succeeded in 0ms:
  1890	    }:
  1891	        raise MintError(
  1892	            f"postcollection_evidence_mismatch: {label} finalized bracket slots mismatch"
  1893	        )
  1894	    receipt_digests = {
  1895	        row.get("receipt_digest")
  1896	        for row in receipts
  1897	        if isinstance(row, Mapping) and _SHA256_RE.fullmatch(str(row.get("receipt_digest")))
  1898	    }
  1899	    if binding.get("capability_receipt_digest") not in receipt_digests:
  1900	        raise MintError(
  1901	            f"postcollection_evidence_mismatch: {label} capability receipt is absent"
  1902	        )
  1903	    endpoints = binding.get("endpoints")
  1904	    if not isinstance(endpoints, Mapping) or set(endpoints) != {"pre", "post"}:
  1905	        raise MintError(
  1906	            f"postcollection_evidence_mismatch: {label} binding endpoints mismatch"
  1907	        )
  1908	    resolved = []
  1909	    for role in ("pre", "post"):
  1910	        endpoint = endpoints.get(role)
  1911	        if not isinstance(endpoint, Mapping) or set(endpoint) != {
  1912	            "attempt_id",
  1913	            "receipt_digest",
  1914	            "content_digest",
  1915	        }:
  1916	            raise MintError(
  1917	                f"postcollection_evidence_mismatch: {label} {role} endpoint schema mismatch"
  1918	            )
  1919	        _sha256(endpoint.get("receipt_digest"), f"{label}.{role}.receipt_digest")
  1920	        _sha256(endpoint.get("content_digest"), f"{label}.{role}.content_digest")
  1921	        matches = [
  1922	            observation
  1923	            for observation in observations
  1924	            if _mapping_attribute(observation, "attempt_id")
  1925	            == endpoint.get("attempt_id")
  1926	            and _mapping_attribute(observation, "receipt_digest")
  1927	            == endpoint.get("receipt_digest")
  1928	            and _mapping_attribute(observation, "content_id")
  1929	            == endpoint.get("content_digest")
  1930	        ]
  1931	        if len(matches) != 1:
  1932	            raise MintError(
  1933	                f"postcollection_evidence_mismatch: {label} {role} receipt/content mismatch"
  1934	            )
  1935	        observation = matches[0]
  1936	        finalized_observation = finalized_slots.get(role)
  1937	        if any(
  1938	            _mapping_attribute(finalized_observation, field)
  1939	            != _mapping_attribute(observation, field)
  1940	            for field in (
  1941	                "sequence",
  1942	                "attempt_id",
  1943	                "receipt_digest",
  1944	                "content_id",
  1945	            )
  1946	        ):
  1947	            raise MintError(
  1948	                f"postcollection_evidence_mismatch: {label} {role} finalized slot mismatch"
  1949	            )
  1950	        for field, expected in (
  1951	            ("disposition", "valid"),
  1952	            ("bracket_session_id", binding.get("session_id")),
  1953	            ("bracket_slot", role),
  1954	            ("bracket_window_id", binding.get("window_id")),
  1955	            ("bracket_plan_id", producer["plan"]["plan_id"]),
  1956	            ("bracket_plan_sha256", producer["plan"]["sha256"]),
  1957	            ("bracket_evidence_root_id", producer["evidence_root_id"]),
  1958	        ):
  1959	            if _mapping_attribute(observation, field) != expected:
  1960	                raise MintError(
  1961	                    f"postcollection_evidence_mismatch: {label} {role} {field} mismatch"
  1962	                )
  1963	        resolved.append(observation)
  1964	    terminal = binding.get("terminal_head")
  1965	    post_sequence = _mapping_attribute(resolved[1], "sequence")
  1966	    post_receipt = _mapping_attribute(resolved[1], "receipt_digest")
  1967	    if (
  1968	        not isinstance(terminal, Mapping)
  1969	        or set(terminal) != {"sequence", "head_digest", "ledger_schema"}
  1970	        or terminal.get("ledger_schema")
  1971	        != "joulewise.calibration_observation_ledger.v1"
  1972	        or isinstance(terminal.get("sequence"), bool)
  1973	        or terminal.get("sequence") != post_sequence
  1974	        or terminal.get("head_digest") != post_receipt
  1975	        or not isinstance(post_sequence, int)
  1976	        or post_sequence < 1
  1977	        or post_sequence > len(receipts)
  1978	        or not isinstance(receipts[post_sequence - 1], Mapping)
  1979	        or receipts[post_sequence - 1].get("receipt_digest") != post_receipt
  1980	    ):
  1981	        raise MintError(
  1982	            f"postcollection_evidence_mismatch: {label} terminal ledger head mismatch"
  1983	        )
  1984	    return resolved[0], resolved[1]
  1985	
  1986	
  1987	def _v2_gate_producer_inventory(
  1988	    producer: Mapping[str, Any],
  1989	    inputs: V2ProducerInputs,
  1990	) -> None:
  1991	    plan = producer["plan"]
  1992	    plan_id = plan["plan_id"]
  1993	    if inputs.plan_sha256 != plan["sha256"]:
  1994	        raise MintError(f"producer {plan_id!r}: calibration plan sha256 mismatch")
  1995	    if inputs.plan_declared_sha256 != plan["declared_sha256"]:
  1996	        raise MintError(f"producer {plan_id!r}: declared plan sha256 mismatch")
  1997	    if inputs.plan_sidecar_sha256 != plan["sidecar_sha256"]:
  1998	        raise MintError(f"producer {plan_id!r}: plan sidecar sha256 mismatch")
  1999	    if inputs.plan.get("plan_id") != plan_id or inputs.plan.get(
  2000	        "calibration_scope"
  2001	    ) != plan["declared_calibration_scope"]:
  2002	        raise MintError(f"producer {plan_id!r}: calibration plan identity mismatch")
  2003	    acceptance = inputs.calibration_acceptance
  2004	    acceptance_pins = producer["calibration_acceptance"]
  2005	    if (
  2006	        not isinstance(acceptance, Mapping)
  2007	        or acceptance.get("acceptance_id") != acceptance_pins["acceptance_id"]
  2008	        or inputs.calibration_acceptance_sha256
  2009	        != acceptance_pins["artifact_sha256"]
  2010	        or acceptance.get("derivation_sha256")
  2011	        != acceptance_pins["derivation_sha256"]
  2012	        or acceptance.get("schema_version")
  2013	        != acceptance_pins["derivation_rule_id"]
  2014	    ):
  2015	        raise MintError(
  2016	            f"producer {plan_id!r}: calibration acceptance evidence mismatch"
  2017	        )
  2018	    components = [
  2019	        component
  2020	        for cell in inputs.cells.values()
  2021	        for component in (cell.absolute, cell.comparative)
  2022	    ]
  2023	    if not components:
  2024	        raise MintError(f"producer {plan_id!r}: no authenticated components")
  2025	    extraction_sha256s = {component.spec_sha256 for component in components}
  2026	    if extraction_sha256s != {producer["extraction_spec"]["sha256"]}:
  2027	        raise MintError(f"producer {plan_id!r}: extraction spec inventory mismatch")
  2028	    unique_members = {
  2029	        member.bundle_id for component in components for member in component.members
  2030	    }
  2031	    if len(unique_members) != producer["extraction_spec"]["member_count"]:
  2032	        raise MintError(f"producer {plan_id!r}: extraction member inventory mismatch")
  2033	    model_hashes = {
  2034	        component.source_regime.get("stack_identity", {}).get(
  2035	            "model_artifact_sha256"
  2036	        )
  2037	        for component in components
  2038	    }
  2039	    runtime_hashes = {
  2040	        component.source_regime.get("stack_identity_sha256")
  2041	        for component in components
  2042	    }
  2043	    config_hashes = {
  2044	        component.scientific_config_identity_sha256 for component in components
  2045	    }
  2046	    runtime_pins = producer["model_runtime_config"]
  2047	    if model_hashes != {runtime_pins["model_artifact_sha256"]}:
  2048	        raise MintError(f"producer {plan_id!r}: model artifact inventory mismatch")
  2049	    if runtime_hashes != {runtime_pins["runtime_identity_sha256"]}:
  2050	        raise MintError(f"producer {plan_id!r}: runtime identity inventory mismatch")
  2051	    if config_hashes != {runtime_pins["config_set_sha256"]}:
  2052	        raise MintError(f"producer {plan_id!r}: config-set inventory mismatch")
  2053	
  2054	
  2055	def _v2_gate_postcollection(
  2056	    *,
  2057	    producer: Mapping[str, Any],
  2058	    cell_pins: Mapping[str, Any],
  2059	    cell_inputs: V2CellComponents,
  2060	    producer_inputs: V2ProducerInputs,
  2061	    ledger_snapshot: Any,
  2062	) -> None:
  2063	    post = cell_pins["postcollection"]
  2064	    pre, post_observation = _v2_authenticate_bracket_binding(
  2065	        producer=producer,
  2066	        inputs=producer_inputs,
  2067	        ledger_snapshot=ledger_snapshot,
  2068	    )
  2069	    expected_binding_sha256 = post["bracket_binding_sha256"]
  2070	    _require_postcollection_evidence_equal(
  2071	        "bracket_binding_sha256",
  2072	        expected_binding_sha256,
  2073	        producer_inputs.bracket_binding_sha256,
  2074	        source="supplied bracket-binding artifact bytes",
  2075	    )
  2076	    binding = producer_inputs.bracket_binding
  2077	    endpoint_fields = {
  2078	        "pre": ("pre_receipt_sha256", "pre_content_sha256"),
  2079	        "post": ("post_receipt_sha256", "post_content_sha256"),
  2080	    }
  2081	    for role, observation in (("pre", pre), ("post", post_observation)):
  2082	        receipt_field, content_field = endpoint_fields[role]
  2083	        _require_postcollection_evidence_equal(
  2084	            receipt_field,
  2085	            post[receipt_field],
  2086	            _mapping_attribute(observation, "receipt_digest"),
  2087	            source=f"authenticated ledger {role} observation",
  2088	        )
  2089	        _require_postcollection_evidence_equal(
  2090	            content_field,
  2091	            post[content_field],
  2092	            _mapping_attribute(observation, "content_id"),
  2093	            source=f"authenticated ledger {role} observation",
  2094	        )
  2095	    _require_postcollection_evidence_equal(
  2096	        "terminal_ledger_head_sha256",
  2097	        post["terminal_ledger_head_sha256"],
  2098	        binding["terminal_head"]["head_digest"],
  2099	        source="authenticated bracket-binding terminal head",
  2100	    )
  2101	    try:
  2102	        observed_drift = abs(
  2103	            _decimal_text(
  2104	                _mapping_attribute(pre, "exact_bound_lexeme_s"),
  2105	                "ledger pre exact_bound_lexeme_s",
  2106	            )
  2107	            - _decimal_text(
  2108	                _mapping_attribute(post_observation, "exact_bound_lexeme_s"),
  2109	                "ledger post exact_bound_lexeme_s",
  2110	            )
  2111	        )
  2112	    except (InvalidOperation, MintError) as exc:
  2113	        raise MintError(
  2114	            "postcollection_evidence_mismatch: ledger endpoint drift is not exact Decimal evidence"
  2115	        ) from exc
  2116	    _require_postcollection_evidence_equal(
  2117	        "observed_drift_s",
  2118	        _decimal_text(post["observed_drift_s"], "postcollection.observed_drift_s"),
  2119	        observed_drift,
  2120	        source="authenticated ledger endpoint bounds",
  2121	    )
  2122	    actual_components = (cell_inputs.absolute, cell_inputs.comparative)
  2123	    for component in actual_components:
  2124	        _require_postcollection_evidence_equal(
  2125	            "extraction_report_sha256",
  2126	            post["extraction_report_sha256"],
  2127	            component.report_sha256,
  2128	            source=f"supplied {component.kind} extraction-report artifact bytes",
  2129	        )
  2130	    records = [
  2131	        _v2_extraction_postcollection_record(
  2132	            component,
  2133	            cell_pins["cell_id"],
  2134	            label=f"{cell_pins['cell_id']}.{component.kind}",
  2135	        )
  2136	        for component in actual_components
  2137	    ]
  2138	    if records[0] != records[1]:
  2139	        raise MintError(
  2140	            "postcollection_evidence_mismatch: component extraction reports disagree"
  2141	        )
  2142	    report_record = records[0]
  2143	    for name in (
  2144	        "observed_drift_s",
  2145	        "applied_allowance_s",
  2146	        "absolute_floor_full_precision",
  2147	        "comparative_floor_full_precision",
  2148	        "operative_floor_full_precision",
  2149	        "absolute_floor_six_decimal",
  2150	        "comparative_floor_six_decimal",
  2151	        "operative_floor_six_decimal",
  2152	    ):
  2153	        _require_postcollection_evidence_equal(
  2154	            name,
  2155	            post[name],
  2156	            report_record[name],
  2157	            source="authenticated extraction-report record",
  2158	        )
  2159	    actual_values = (
  2160	        cell_inputs.absolute.cell.get("floor", {}).get(
  2161	            "drift_widened_guarded_floor_j"
  2162	        ),
  2163	        cell_inputs.comparative.cell.get("floor", {}).get(
  2164	            "drift_widened_guarded_floor_j"
  2165	        ),
  2166	    )
  2167	    expected_values = (
  2168	        _decimal_text(
  2169	            post["absolute_floor_full_precision"],
  2170	            "postcollection.absolute_floor_full_precision",
  2171	        ),
  2172	        _decimal_text(
  2173	            post["comparative_floor_full_precision"],
  2174	            "postcollection.comparative_floor_full_precision",
  2175	        ),
  2176	    )
  2177	    for name, actual, expected in zip(
  2178	        ("absolute", "comparative"), actual_values, expected_values
  2179	    ):
  2180	        if isinstance(actual, bool) or not isinstance(actual, int | float):
  2181	            raise MintError(
  2182	                f"postcollection_evidence_mismatch: {name} extraction value is not numeric"
  2183	            )
  2184	        if Decimal(str(actual)) != expected:
  2185	            raise MintError(
  2186	                f"postcollection_evidence_mismatch: {name} full-precision value mismatch"
  2187	            )
  2188	
  2189	
  2190	def _v2_allowed_families(
  3000	            ) from exc
  3001	        if not isinstance(plan, Mapping):
  3002	            raise MintError(f"producer {plan_id!r} calibration plan must be an object")
  3003	        if hashlib.sha256(plan_raw).hexdigest() != producer["plan"]["sha256"]:
  3004	            raise MintError(f"producer {plan_id!r} calibration plan sha256 mismatch")
  3005	        sidecar_path = Path(
  3006	            _string(
  3007	                manifest_row["calibration_plan_sidecar"],
  3008	                f"v2 input manifest producer {plan_id}.calibration_plan_sidecar",
  3009	            )
  3010	        )
  3011	        try:
  3012	            sidecar_raw = sidecar_path.read_bytes()
  3013	            sidecar_text = sidecar_raw.decode("utf-8")
  3014	        except OSError as exc:
  3015	            raise MintError(
  3016	                f"producer {plan_id!r} plan sidecar cannot be read: "
  3017	                f"{exc.strerror or type(exc).__name__}"
  3018	            ) from exc
  3019	        except UnicodeDecodeError as exc:
  3020	            raise MintError(
  3021	                f"producer {plan_id!r} plan sidecar is not UTF-8"
  3022	            ) from exc
  3023	        sidecar_parts = sidecar_text.strip().split()
  3024	        if (
  3025	            len(sidecar_parts) != 2
  3026	            or sidecar_parts[0] != producer["plan"]["declared_sha256"]
  3027	            or sidecar_parts[0] != hashlib.sha256(plan_raw).hexdigest()
  3028	            or sidecar_parts[1] != plan_path.name
  3029	            or hashlib.sha256(sidecar_raw).hexdigest()
  3030	            != producer["plan"]["sidecar_sha256"]
  3031	        ):
  3032	            raise MintError(f"producer {plan_id!r} plan sidecar pins mismatch")
  3033	        bracket_path = Path(
  3034	            _string(
  3035	                manifest_row["bracket_binding"],
  3036	                f"v2 input manifest producer {plan_id}.bracket_binding",
  3037	            )
  3038	        )
  3039	        try:
  3040	            bracket_raw = bracket_path.read_bytes()
  3041	            bracket_binding = json.loads(
  3042	                bracket_raw.decode("utf-8"),
  3043	                object_pairs_hook=_reject_duplicate_keys,
  3044	                parse_constant=_reject_nonfinite_json,
  3045	            )
  3046	        except OSError as exc:
  3047	            raise MintError(
  3048	                f"producer {plan_id!r} bracket binding cannot be read: "
  3049	                f"{exc.strerror or type(exc).__name__}"
  3050	            ) from exc
  3051	        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
  3052	            raise MintError(
  3053	                f"producer {plan_id!r} bracket binding is invalid JSON: {exc}"
  3054	            ) from exc
  3055	        if not isinstance(bracket_binding, Mapping):
  3056	            raise MintError(f"producer {plan_id!r} bracket binding must be an object")
  3057	        cells = manifest_row["cells"]
  3058	        if not isinstance(cells, list) or len(cells) != 2:
  3059	            raise MintError(
  3060	                f"v2 input manifest producer {plan_id!r} must contain two cells"
  3061	            )
  3062	        cell_rows: dict[str, Mapping[str, Any]] = {}
  3063	        for cell_index, cell_value in enumerate(cells):
  3064	            cell_label = (
  3065	                f"v2 input manifest producer {plan_id}.cells[{cell_index}]"
  3066	            )
  3067	            cell_row = _object(
  3068	                cell_value,
  3069	                cell_label,
  3070	                {
  3071	                    "role",
  3072	                    "absolute",
  3073	                    "comparative",
  3074	                    "allowed_consumer_condition_families",
  3075	                },
  3076	            )
  3077	            role = _string(cell_row["role"], f"{cell_label}.role")
  3078	            if role in cell_rows:
  3079	                raise MintError(f"producer {plan_id!r} cell roles must be unique")
  3080	            cell_rows[role] = cell_row
  3081	        if set(cell_rows) != {"decode", "prefill"}:
  3082	            raise MintError(
  3083	                f"producer {plan_id!r} input cells must be decode and prefill"
  3084	            )
  3085	
  3086	        authenticated_cells: dict[str, V2CellComponents] = {}
  3087	        producer_evidence_root: Path | None = None
  3088	        for cell_pins in producer["cells"]:
  3089	            role = cell_pins["role"]
  3090	            cell_row = cell_rows[role]
  3091	            configured = _v2_mint_pinset(producer, cell_pins)
  3092	            core = _configured_core(
  3093	                configured,
  3094	                pinset_path=pinset_path,
  3095	                expected_pinset_sha256=pinset_sha256,
  3096	            )
  3097	            authenticated = []
  3098	            for component_name, expected_kind in (
  3099	                ("absolute", "absolute"),
  3100	                ("comparative", "comparative"),
  3101	            ):
  3102	                paths = _v2_component_input_paths(
  3103	                    cell_row[component_name],
  3104	                    f"producer {plan_id}.{role}.{component_name}",
  3105	                )
  3106	                root_id = cell_pins[component_name]["evidence_root_id"]
  3107	                existing_root = evidence_roots.get(root_id)
  3108	                if existing_root is not None and existing_root.resolve() != (
  3109	                    paths.evidence_root.resolve()
  3110	                ):
  3111	                    raise MintError(
  3112	                        f"evidence-root id {root_id!r} maps to multiple paths"
  3113	                    )
  3114	                evidence_roots[root_id] = paths.evidence_root
  3115	                if (
  3116	                    producer_evidence_root is not None
  3117	                    and producer_evidence_root.resolve()
  3118	                    != paths.evidence_root.resolve()
  3119	                ):
  3120	                    raise MintError(
  3121	                        f"producer {plan_id!r} components map to multiple evidence roots"
  3122	                    )
  3123	                producer_evidence_root = paths.evidence_root
  3124	                try:
  3125	                    component = core._authenticate_component(
  3126	                        core.ComponentPaths(
  3127	                            evidence_root_id=root_id,
  3128	                            evidence_root=paths.evidence_root,
  3129	                            report_path=paths.report_path,
  3130	                            spec_path=paths.spec_path,
  3131	                            order_manifest_path=paths.order_manifest_path,
  3132	                            calibration_cell_id=cell_pins[component_name][
  3133	                                "calibration_cell_id"
  3134	                            ],
  3135	                            expected_kind=expected_kind,
  3136	                        ),
  3137	                        expected_cell_id=cell_pins[component_name][
  3138	                            "calibration_cell_id"
  3139	                        ],
  3140	                        expected_basis_sha256=cell_pins[component_name][
  3141	                            "evaluation_basis_sha256"
  3142	                        ],
  3143	                        strict_validator=strict_validator,
  3144	                        expected_consumption_semantics_id=cell_pins[
  3145	                            component_name
  3146	                        ]["consumption_semantics_id"],
  3147	                        calibration_ledger_snapshot=ledger_snapshot,
  3148	                    )
  3149	                except core.MintError as exc:
  3150	                    raise MintError(str(exc)) from exc
  3151	                authenticated.append(component)
  3152	            families = cell_row["allowed_consumer_condition_families"]
  3153	            if not isinstance(families, list):
  3154	                raise MintError(
  3155	                    f"producer {plan_id}.{role} allowed families must be an array"
  3156	                )
  3157	            authenticated_cells[role] = V2CellComponents(
  3158	                absolute=authenticated[0],
  3159	                comparative=authenticated[1],
  3160	                allowed_consumer_condition_families=tuple(families),
  3161	            )
  3162	        if consumption_semantics_id is not None:
  3163	            pinned_semantics = {
  3164	                cell[component_name]["consumption_semantics_id"]
  3165	                for cell in producer["cells"]
  3166	                for component_name in ("absolute", "comparative")
  3167	            }
  3168	            if pinned_semantics != {consumption_semantics_id}:
  3169	                raise MintError(
  3170	                    "explicit v2 consumption semantics dispatch contradicts "
  3171	                    "per-component pins"
  3172	                )
  3173	        if producer_evidence_root is None:
  3174	            raise MintError(f"producer {plan_id!r} has no authenticated evidence root")
  3175	        result[plan_id] = V2ProducerInputs(
  3176	            plan=dict(plan),
  3177	            cells=authenticated_cells,
  3178	            evidence_root=producer_evidence_root,
  3179	            plan_sha256=hashlib.sha256(plan_raw).hexdigest(),
  3180	            plan_declared_sha256=sidecar_parts[0],
  3181	            plan_sidecar_sha256=hashlib.sha256(sidecar_raw).hexdigest(),
  3182	            calibration_acceptance=dict(acceptance),
  3183	            calibration_acceptance_sha256=acceptance_sha256,
  3184	            bracket_binding=dict(bracket_binding),
  3185	            bracket_binding_sha256=hashlib.sha256(bracket_raw).hexdigest(),
  3186	        )
  3187	    return result, evidence_roots, ledger_snapshot
  3188	
  3189	
  3190	def mint_multi_cell_floor_artifact(
  3191	    *,
  3192	    pinset_path: Path,
  3193	    pinset_sha256: str,
  3194	    input_manifest_path: Path,
  3195	    floor_path: Path,
  3196	    statement_path: Path,
  3197	    project_commit: str,
  3198	    project_tree_state: str,
  3199	    strict_validator: StrictValidator,
  3200	    consumption_semantics_id: str | None = None,
  3201	) -> Mapping[str, Any]:
  3202	    """Authenticate all v2 sources, mint once, rebind, and write exclusively."""
  3203	
  3204	    loaded = load_pinset(pinset_path, pinset_sha256)
  3205	    if not isinstance(loaded, V2Pinset):
  3206	        raise MintError("multi-cell floor mint requires a final v2 pinset")
  3207	    _validate_v2_pin_hashes(loaded)
  3208	    inputs, evidence_roots, ledger_snapshot = _authenticate_v2_inputs(
  3209	        pinset=loaded,
  3210	        pinset_path=pinset_path,
  3210	        pinset_path=pinset_path,
  3211	        pinset_sha256=pinset_sha256,
  3212	        input_manifest_path=input_manifest_path,
  3213	        strict_validator=strict_validator,
  3214	        consumption_semantics_id=consumption_semantics_id,
  3215	    )
  3216	    artifact, components = _build_v2_artifacts(
  3217	        pinset=loaded,
  3218	        pinset_path=pinset_path,
  3219	        pinset_sha256=pinset_sha256,
  3220	        producer_inputs=inputs,
  3221	        calibration_ledger_snapshot=ledger_snapshot,
  3222	        project_commit=project_commit,
  3223	        project_tree_state=project_tree_state,
  3224	    )
  3225	    for producer, component, expected in zip(
  3226	        loaded.value["producer_plans"],
  3227	        components,
  3228	        loaded.value["aggregate"]["component_artifacts"],
  3229	    ):
  3230	        observed = _artifact_sha256(component)
  3231	        if observed != expected["sha256"]:
  3232	            raise MintError(
  3233	                "aggregate/component hash mismatch: component artifact "
  3234	                f"{expected['plan_id']!r} expected {expected['sha256']}, observed {observed}"
  3235	            )
  3236	        cells_by_id = {
  3237	            cell["cell_id"]: cell for cell in component["cells"]
  3238	        }
  3239	        groups_by_id = {
  3240	            group["transport_group_id"]: group
  3241	            for group in component["transport_groups"]
  3242	        }
  3243	        for cell_pins in producer["cells"]:
  3244	            configured = _v2_mint_pinset(producer, cell_pins)
  3245	            core = _configured_core(
  3246	                configured,
  3247	                pinset_path=pinset_path,
  3248	                expected_pinset_sha256=pinset_sha256,
  3249	            )
  3250	            single_cell_component = copy.deepcopy(dict(component))
  3251	            single_cell_component["cells"] = [
  3252	                copy.deepcopy(cells_by_id[cell_pins["cell_id"]])
  3253	            ]
  3254	            single_cell_component["transport_groups"] = [
  3255	                copy.deepcopy(
  3256	                    groups_by_id[cell_pins["transport_group_id"]]
  3257	                )
  3258	            ]
  3259	            try:
  3260	                core.bind_floor_artifact_evidence(
  3261	                    single_cell_component,
  3262	                    floor_path,
  3263	                    evidence_roots,
  3264	                    strict_validator=strict_validator,
  3265	                    calibration_ledger_snapshot=ledger_snapshot,
  3266	                )
  3267	            except core.MintError as exc:
  3268	                raise MintError(str(exc)) from exc
  3269	    errors = validate_floor_artifact(
  3270	        artifact=artifact,
  3271	        pinset_path=pinset_path,
  3272	        pinset_sha256=pinset_sha256,
  3273	    )
  3274	    if errors:
  3275	        raise MintError(f"post-bind v2 artifact validation failed: {errors[0]}")
  3276	    output_core = _fresh_original_core()
  3277	    try:
  3278	        output_core.write_outputs_exclusive(artifact, floor_path, statement_path)
  3279	    except output_core.MintError as exc:
  3280	        raise MintError(str(exc)) from exc
  3281	    return artifact
  3282	
  3283	
  3284	def _parser() -> argparse.ArgumentParser:
  3285	    parser = argparse.ArgumentParser(description=__doc__)
  3286	    parser.add_argument("--pinset", required=True, type=Path)
  3287	    parser.add_argument("--pinset-sha256", required=True)
  3288	    parser.add_argument("--artifact-id")
  3289	    parser.add_argument("--out", required=True, type=Path)
  3290	    parser.add_argument("--single-count-out", required=True, type=Path)
  3291	    parser.add_argument("--v2-input-manifest", type=Path)
  3292	    parser.add_argument("--calibration-plan", type=Path)
  3293	    parser.add_argument("--calibration-plan-relative-path")
  3294	    parser.add_argument("--absolute-root", type=Path)
  3295	    parser.add_argument("--absolute-report", type=Path)
  3296	    parser.add_argument("--absolute-spec", type=Path)
  3297	    parser.add_argument("--absolute-order-manifest", type=Path)
  3298	    parser.add_argument("--comparative-root", type=Path)
  3299	    parser.add_argument("--comparative-report", type=Path)
  3300	    parser.add_argument("--comparative-spec", type=Path)
  3301	    parser.add_argument(
  3302	        "--comparative-order-manifest", type=Path
  3303	    )
  3304	    parser.add_argument("--project-commit", required=True)
  3305	    parser.add_argument(
  3306	        "--project-tree-state", choices=("clean", "dirty"), required=True
  3307	    )
  3308	    parser.add_argument(
  3309	        "--consumption-semantics-id",
  3310	        choices=tuple(sorted(_SEMANTICS_IDS)),
  3311	        help=(
  3312	            "optional exact semantics dispatch; when supplied both component "
  3313	            "reports must use this id"
  3314	        ),
  3315	    )
  3316	    return parser
  3317	
  3318	
  3319	def main(argv: list[str] | None = None) -> int:
  3320	    from joulewise.cli import validate_bundle
  3321	
  3322	    args = _parser().parse_args(argv)
  3323	    try:
  3324	        loaded = load_pinset(args.pinset, args.pinset_sha256)
  3325	        if isinstance(loaded, V2Pinset):
  3326	            if args.v2_input_manifest is None:
  3327	                raise MintError("final v2 pinset requires --v2-input-manifest")
  3328	            mint_multi_cell_floor_artifact(
  3329	                pinset_path=args.pinset,
  3330	                pinset_sha256=args.pinset_sha256,
  3331	                input_manifest_path=args.v2_input_manifest,
  3332	                floor_path=args.out,
  3333	                statement_path=args.single_count_out,
  3334	                project_commit=args.project_commit,
  3335	                project_tree_state=args.project_tree_state,
  3336	                strict_validator=lambda path, strict: validate_bundle(
  3337	                    path, strict=strict
  3338	                ),
  3339	                consumption_semantics_id=args.consumption_semantics_id,
  3340	            )
  3341	            return 0
  3342	        legacy_fields = {
  3343	            "--artifact-id": args.artifact_id,
  3344	            "--calibration-plan": args.calibration_plan,
  3345	            "--calibration-plan-relative-path": (
  3346	                args.calibration_plan_relative_path
  3347	            ),
  3348	            "--absolute-root": args.absolute_root,
  3349	            "--absolute-report": args.absolute_report,
  3350	            "--absolute-spec": args.absolute_spec,
  3351	            "--absolute-order-manifest": args.absolute_order_manifest,
  3352	            "--comparative-root": args.comparative_root,
  3353	            "--comparative-report": args.comparative_report,
  3354	            "--comparative-spec": args.comparative_spec,
  3355	            "--comparative-order-manifest": (
  3356	                args.comparative_order_manifest
  3357	            ),
  3358	        }
  3359	        missing = [name for name, value in legacy_fields.items() if value is None]
  3360	        if missing:
  3361	            raise MintError(
  3362	                "v1 pinset requires arguments: " + ", ".join(missing)
  3363	            )
  3364	        mint_floor_artifact(
  3365	            pinset_path=args.pinset,
  3366	            pinset_sha256=args.pinset_sha256,
  3367	            artifact_id=args.artifact_id,
  3368	            floor_path=args.out,
  3369	            statement_path=args.single_count_out,
  3370	            calibration_plan_path=args.calibration_plan,
  3371	            calibration_plan_relative_path=(
  3372	                args.calibration_plan_relative_path
  3373	            ),
  3374	            absolute_inputs=ComponentInputs(
  3375	                evidence_root=args.absolute_root,
  3376	                report_path=args.absolute_report,
  3377	                spec_path=args.absolute_spec,
  3378	                order_manifest_path=args.absolute_order_manifest,
  3379	            ),
  3380	            comparative_inputs=ComponentInputs(
  3381	                evidence_root=args.comparative_root,
  3382	                report_path=args.comparative_report,
  3383	                spec_path=args.comparative_spec,
  3384	                order_manifest_path=args.comparative_order_manifest,
  3385	            ),
  3386	            project_commit=args.project_commit,
  3387	            project_tree_state=args.project_tree_state,
  3388	            strict_validator=lambda path, strict: validate_bundle(
  3389	                path, strict=strict
  3390	            ),
  3391	            consumption_semantics_id=args.consumption_semantics_id,
  3392	        )
  3393	    except MintError as exc:
  3394	        print(f"error: {exc}", file=sys.stderr)
  3395	        return 2
  3396	    return 0
  3397	
  3398	
  3399	if __name__ == "__main__":
  3400	    raise SystemExit(main())
  3400	    raise SystemExit(main())

exec
/bin/zsh -lc "rg -n '"'^def (_authenticate_component|load_calibration_acceptance_bound|load_calibration_ledger_snapshot|authenticate|bind_floor_artifact_evidence)|class CalibrationLedgerSnapshot|head_pin|receipt_digest|content_id|report_sha256|spec_sha256|order_manifest_sha256'"' scripts/mint_floor_artifact.py joulewise -g '*.py' | head -300; nl -ba scripts/mint_floor_artifact.py | sed -n '230,620p'; nl -ba scripts/mint_floor_artifact.py | sed -n '620,1040p'" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u3
 succeeded in 0ms:
scripts/mint_floor_artifact.py:160:    report_sha256: str
scripts/mint_floor_artifact.py:162:    spec_sha256: str
scripts/mint_floor_artifact.py:164:    order_manifest_sha256: str
scripts/mint_floor_artifact.py:1012:def _authenticate_component(
scripts/mint_floor_artifact.py:1218:        report_sha256=_sha256(report_raw),
scripts/mint_floor_artifact.py:1220:        spec_sha256=_sha256(spec_raw),
scripts/mint_floor_artifact.py:1222:        order_manifest_sha256=_sha256(order_raw),
scripts/mint_floor_artifact.py:1475:            "sha256": component.order_manifest_sha256,
scripts/mint_floor_artifact.py:1478:        "extraction_report": {"sha256": component.report_sha256},
scripts/mint_floor_artifact.py:1479:        "extraction_spec": {"sha256": component.spec_sha256},
scripts/mint_floor_artifact.py:1664:def bind_floor_artifact_evidence(
joulewise/powermetrics_fiducial.py:378:def authenticate_protocol_schedule(
joulewise/detection_floor.py:1490:    "evaluation_basis_members", "extraction_spec_sha256",
joulewise/detection_floor.py:1492:    "order_manifest_id", "order_manifest_sha256", "consumption_semantics_id",
joulewise/detection_floor.py:1502:    "extraction_report_sha256", "absolute_floor_full_precision",
joulewise/detection_floor.py:1777:                    or not _is_hex(component.get("extraction_spec_sha256"))
joulewise/detection_floor.py:1778:                    or component.get("extraction_spec_sha256")
joulewise/detection_floor.py:1789:                    or not _is_hex(component.get("order_manifest_sha256"))
joulewise/detection_floor.py:1889:                        "extraction_report_sha256",
joulewise/calibration_ledger.py:153:def content_id_from_artifact_hashes(artifact_sha256: Mapping[str, Any]) -> str | None:
joulewise/calibration_ledger.py:183:    return {key: value for key, value in receipt.items() if key != "receipt_digest"}
joulewise/calibration_ledger.py:186:def _receipt_digest(receipt: Mapping[str, Any]) -> str:
joulewise/calibration_ledger.py:193:    receipt_digest: str
joulewise/calibration_ledger.py:195:    content_id: str | None
joulewise/calibration_ledger.py:219:class CalibrationLedgerSnapshot:
joulewise/calibration_ledger.py:246:            if observation.content_id is not None:
joulewise/calibration_ledger.py:247:                grouped.setdefault(observation.content_id, []).append(observation)
joulewise/calibration_ledger.py:282:    head_pin: Mapping[str, Any]
joulewise/calibration_ledger.py:306:    content_id: str
joulewise/calibration_ledger.py:339:        "content_id",
joulewise/calibration_ledger.py:347:        "receipt_digest",
joulewise/calibration_ledger.py:406:        or not _is_sha256(receipt.get("receipt_digest"))
joulewise/calibration_ledger.py:407:        or receipt.get("receipt_digest") != _receipt_digest(receipt)
joulewise/calibration_ledger.py:410:    content_id = receipt.get("content_id")
joulewise/calibration_ledger.py:411:    if content_id is not None and not _is_sha256(content_id):
joulewise/calibration_ledger.py:419:            and content_id is None
joulewise/calibration_ledger.py:446:        return content_id == content_id_from_artifact_hashes(artifacts)
joulewise/calibration_ledger.py:448:        content_id is None
joulewise/calibration_ledger.py:449:        or content_id_from_artifact_hashes(artifacts) != content_id
joulewise/calibration_ledger.py:459:def _head_pin(value: object) -> tuple[int, str] | None:
joulewise/calibration_ledger.py:527:            or value["receipt_digest"] in seen_digests
joulewise/calibration_ledger.py:531:        predecessor = value["receipt_digest"]
joulewise/calibration_ledger.py:577:        content_id = receipt.get("content_id")
joulewise/calibration_ledger.py:579:        if isinstance(content_id, str):
joulewise/calibration_ledger.py:588:            previous = content_classification.get(content_id)
joulewise/calibration_ledger.py:591:            content_classification[content_id] = classification
joulewise/calibration_ledger.py:595:                receipt_digest=str(receipt["receipt_digest"]),
joulewise/calibration_ledger.py:597:                content_id=str(content_id) if isinstance(content_id, str) else None,
joulewise/calibration_ledger.py:637:def load_calibration_ledger_snapshot(
joulewise/calibration_ledger.py:639:    head_pin_path: Path = DEFAULT_HEAD_PIN_PATH,
joulewise/calibration_ledger.py:658:    head_pin_path = Path(head_pin_path)
joulewise/calibration_ledger.py:661:        pin_raw = head_pin_path.read_bytes()
joulewise/calibration_ledger.py:666:    pin = _head_pin(pin_value)
joulewise/calibration_ledger.py:692:        and _committed_pin_bytes(head_pin_path, repo_root) != pin_raw
joulewise/calibration_ledger.py:699:        str(receipts[-1]["receipt_digest"]) if receipts else GENESIS_DIGEST
joulewise/calibration_ledger.py:719:                and receipts[baseline_sequence - 1]["receipt_digest"]
joulewise/calibration_ledger.py:747:    content_id: str | None,
joulewise/calibration_ledger.py:764:        "content_id": content_id,
joulewise/calibration_ledger.py:777:    receipt["receipt_digest"] = _receipt_digest(receipt)
joulewise/calibration_ledger.py:846:            "content_id",
joulewise/calibration_ledger.py:852:        content_id = member.get("content_id")
joulewise/calibration_ledger.py:858:            or not _is_sha256(content_id)
joulewise/calibration_ledger.py:862:            or content_id_from_artifact_hashes(artifacts) != content_id
joulewise/calibration_ledger.py:868:                "historical import attempt_id collision; content_id tiebreak is "
joulewise/calibration_ledger.py:871:        if str(content_id) in by_content:
joulewise/calibration_ledger.py:872:            raise CalibrationLedgerError("historical import content_id is duplicated")
joulewise/calibration_ledger.py:874:        by_content[str(content_id)] = member
joulewise/calibration_ledger.py:881:    expected_content_ids: set[str],
joulewise/calibration_ledger.py:892:    if set(members) != expected_content_ids:
joulewise/calibration_ledger.py:897:    for content_id, locator in members.items():
joulewise/calibration_ledger.py:898:        if not _is_sha256(content_id) or not isinstance(locator, str) or not locator:
joulewise/calibration_ledger.py:903:        result[str(content_id)] = path
joulewise/calibration_ledger.py:1049:    content_id = content_id_from_artifact_hashes(primary_hashes)
joulewise/calibration_ledger.py:1050:    if content_id is None:
joulewise/calibration_ledger.py:1061:        return content_id, None, f"{directory}: custody is outside checkout root: {exc}"
joulewise/calibration_ledger.py:1066:        return content_id, None, f"{directory}: hash-complete custody is missing: {exc}"
joulewise/calibration_ledger.py:1082:        return content_id, None, f"{directory}: manifest artifact hash mismatch"
joulewise/calibration_ledger.py:1091:        return content_id, None, f"{directory}: evidence artifact hash mismatch"
joulewise/calibration_ledger.py:1099:        return content_id, None, f"{directory}: attempt identity mismatch"
joulewise/calibration_ledger.py:1102:        return content_id, None, f"{directory}: full T1 binding is incomplete"
joulewise/calibration_ledger.py:1106:        return content_id, None, str(exc)
joulewise/calibration_ledger.py:1110:        return content_id, None, f"{directory}: capture time lexeme is invalid"
joulewise/calibration_ledger.py:1112:        return content_id, None, f"{directory}: bound lexeme is invalid"
joulewise/calibration_ledger.py:1114:        return content_id, None, f"{directory}: capture time is missing"
joulewise/calibration_ledger.py:1116:        content_id,
joulewise/calibration_ledger.py:1119:            content_id=content_id,
joulewise/calibration_ledger.py:1147:        content_id, candidate, error = _inspect_historical_candidate(
joulewise/calibration_ledger.py:1153:            complete.setdefault(candidate.content_id, []).append(candidate)
joulewise/calibration_ledger.py:1155:            if content_id is None:
joulewise/calibration_ledger.py:1158:                incomplete.setdefault(content_id, []).append(error)
joulewise/calibration_ledger.py:1190:            f"historical import table omits authenticated content_id {extra_ids[0]}"
joulewise/calibration_ledger.py:1197:            f"historical import content_id is missing: {missing_ids[0]}"
joulewise/calibration_ledger.py:1200:    for content_id in sorted(expected_ids):
joulewise/calibration_ledger.py:1202:            complete[content_id], key=lambda item: item.custody_sort_key
joulewise/calibration_ledger.py:1204:        member = table_by_content[content_id]
joulewise/calibration_ledger.py:1207:                f"{content_id}: attempt_id differs from disposition table"
joulewise/calibration_ledger.py:1211:                f"{content_id}: artifact hashes differ from disposition table"
joulewise/calibration_ledger.py:1213:        members[content_id] = candidate.custody_locator
joulewise/calibration_ledger.py:1245:        expected_content_ids=set(table_by_content),
joulewise/calibration_ledger.py:1249:    for content_id, locator in pinned.items():
joulewise/calibration_ledger.py:1259:        if observed_id != content_id:
joulewise/calibration_ledger.py:1261:                f"pinned custody content_id mismatch: {content_id}"
joulewise/calibration_ledger.py:1263:        selected_by_content[content_id] = candidate
joulewise/calibration_ledger.py:1292:    for content_id, member in table_by_content.items():
joulewise/calibration_ledger.py:1293:        candidate = selected_by_content[content_id]
joulewise/calibration_ledger.py:1296:                f"{content_id}: attempt_id differs from disposition table"
joulewise/calibration_ledger.py:1300:                f"{content_id}: artifact hashes differ from disposition table"
joulewise/calibration_ledger.py:1304:    # Attempt ids are contractually unique. content_id is the deterministic
joulewise/calibration_ledger.py:1306:    selected.sort(key=lambda item: (item[0].attempt_id, item[0].content_id))
joulewise/calibration_ledger.py:1315:            content_id=None,
joulewise/calibration_ledger.py:1331:        predecessor = str(reservation["receipt_digest"])
joulewise/calibration_ledger.py:1337:            content_id=candidate.content_id,
joulewise/calibration_ledger.py:1349:        predecessor = str(finalization["receipt_digest"])
joulewise/calibration_ledger.py:1357:    pin = head_pin_for_receipt(final)
joulewise/calibration_ledger.py:1361:        head_digest=str(final["receipt_digest"]),
joulewise/calibration_ledger.py:1362:        head_pin=_frozen_mapping(pin),
joulewise/calibration_ledger.py:1370:    head_pin_path: Path,
joulewise/calibration_ledger.py:1378:        pin_raw = Path(head_pin_path).read_bytes()
joulewise/calibration_ledger.py:1382:    if _head_pin(pin_value) != (0, GENESIS_DIGEST):
joulewise/calibration_ledger.py:1386:        and _committed_pin_bytes(Path(head_pin_path), Path(repo_root)) != pin_raw
joulewise/calibration_ledger.py:1502:    head_pin_path: Path,
joulewise/calibration_ledger.py:1521:    pin = Path(head_pin_path)
joulewise/calibration_ledger.py:1648:    head_pin_path: Path = DEFAULT_HEAD_PIN_PATH,
joulewise/calibration_ledger.py:1661:    pin_path = Path(head_pin_path)
joulewise/calibration_ledger.py:1667:    pin = _head_pin(pin_value)
joulewise/calibration_ledger.py:1675:        predecessor = receipts[-1]["receipt_digest"] if receipts else GENESIS_DIGEST
joulewise/calibration_ledger.py:1691:            content_id=None,
joulewise/calibration_ledger.py:1721:    content_id = content_id_from_artifact_hashes(artifacts)
joulewise/calibration_ledger.py:1749:        predecessor = receipts[-1]["receipt_digest"] if receipts else GENESIS_DIGEST
joulewise/calibration_ledger.py:1755:            content_id=content_id,
joulewise/calibration_ledger.py:1768:def head_pin_for_receipt(receipt: Mapping[str, Any]) -> dict[str, Any]:
joulewise/calibration_ledger.py:1775:        "head_digest": str(receipt["receipt_digest"]),
joulewise/calibration_ledger.py:1807:    "content_id_from_artifact_hashes",
joulewise/calibration_ledger.py:1810:    "head_pin_for_receipt",
joulewise/calibration_bracketing.py:24:    content_id_from_artifact_hashes,
joulewise/calibration_bracketing.py:88:    content_id: str | None = None
joulewise/calibration_bracketing.py:89:    ledger_receipt_digest: str | None = None
joulewise/calibration_bracketing.py:104:            "content_id": self.content_id,
joulewise/calibration_bracketing.py:105:            "ledger_receipt_digest": self.ledger_receipt_digest,
joulewise/calibration_bracketing.py:305:            != {"content_id", "epoch_id", "disposition", "attempt_id"}
joulewise/calibration_bracketing.py:306:            or not _valid_sha256(observation.get("content_id"))
joulewise/calibration_bracketing.py:313:        prior_ids.append(observation["content_id"])
joulewise/calibration_bracketing.py:337:    member_content_ids = {
joulewise/calibration_bracketing.py:338:        content_id_from_artifact_hashes(
joulewise/calibration_bracketing.py:348:    if None in member_content_ids or not member_content_ids.issubset(set(prior_ids)):
joulewise/calibration_bracketing.py:431:def load_calibration_acceptance_bound(
joulewise/calibration_bracketing.py:667:    if observation.disposition != "valid" or observation.content_id is None:
joulewise/calibration_bracketing.py:687:        or content_id_from_artifact_hashes(observation.artifact_sha256)
joulewise/calibration_bracketing.py:688:        != observation.content_id
joulewise/calibration_bracketing.py:707:        content_id=observation.content_id,
joulewise/calibration_bracketing.py:708:        ledger_receipt_digest=observation.receipt_digest,
joulewise/calibration_bracketing.py:758:            row["content_id"],
joulewise/calibration_bracketing.py:771:        if observation.content_id is None or len(epoch_ids) != 1:
joulewise/calibration_bracketing.py:776:                observation.content_id,
joulewise/calibration_bracketing.py:975:            observation.content_id,
joulewise/calibration_bracketing.py:976:            observation.receipt_digest,
joulewise/calibration_bracketing.py:985:            candidate.content_id,
joulewise/calibration_bracketing.py:986:            candidate.ledger_receipt_digest,
joulewise/calibration_bracketing.py:1004:            or candidate.content_id != observation.content_id
joulewise/calibration_bracketing.py:1005:            or candidate.ledger_receipt_digest != observation.receipt_digest
joulewise/calibration_bracketing.py:1040:        observation["content_id"]
joulewise/calibration_bracketing.py:1044:        observation.content_id: observation
joulewise/calibration_bracketing.py:1046:        if observation.content_id is not None
joulewise/calibration_bracketing.py:1049:        content_id: observation
joulewise/calibration_bracketing.py:1050:        for content_id, observation in distinct_observations.items()
joulewise/calibration_bracketing.py:1055:        for content_id, observation in sorted(distinct_live_observations.items())
joulewise/calibration_bracketing.py:1056:        if content_id not in prior_ids
joulewise/calibration_bracketing.py:1065:                if observation.content_id is None
joulewise/bundle.py:650:                content_identity = content_digest.digest()
joulewise/bundle.py:655:                content_identity = hashlib.sha256(target).digest()
joulewise/bundle.py:665:        _length_framed(digest, content_identity)
joulewise/output_identity.py:69:    "strict_validation_state", "strict_validation_report_sha256",
joulewise/output_identity.py:200:        "strict_validation_report_sha256": strict_hash,
joulewise/output_identity.py:669:            "strict_validation_report_sha256",
joulewise/output_identity.py:693:        if (bundle["strict_validation_report_sha256"] is None) != strict_missing or (bundle["strict_validation_state"] == "unavailable") != strict_missing:
joulewise/analysis_engine/inputs.py:458:def authenticate_floor_artifact_bytes(
joulewise/analysis_engine/inputs.py:1242:def bind_floor_artifact_evidence(
   230	        path.is_absolute()
   231	        or "\\" in value
   232	        or value != path.as_posix()
   233	        or any(part in {"", ".", ".."} for part in path.parts)
   234	        or _WINDOWS_ABSOLUTE_RE.match(value)
   235	    ):
   236	        raise MintError(f"{label} must be a safe-relative POSIX path")
   237	    return value
   238	
   239	
   240	def _assert_path_independent(value: object, label: str = "artifact") -> None:
   241	    """Reject absolute paths and validate every persisted relative_path."""
   242	
   243	    if isinstance(value, Mapping):
   244	        for key, child in value.items():
   245	            child_label = f"{label}.{key}"
   246	            if key == "relative_path":
   247	                _safe_relative_posix(child, child_label)
   248	            _assert_path_independent(child, child_label)
   249	        return
   250	    if isinstance(value, list):
   251	        for index, child in enumerate(value):
   252	            _assert_path_independent(child, f"{label}[{index}]")
   253	        return
   254	    if isinstance(value, str) and (
   255	        value.startswith("/") or _WINDOWS_ABSOLUTE_RE.match(value)
   256	    ):
   257	        raise MintError(f"{label}: absolute paths may not be persisted")
   258	
   259	
   260	def _metric_value(summary: Mapping[str, Any]) -> float:
   261	    phases = summary.get("phase_energy_j")
   262	    value = phases.get("decode") if isinstance(phases, Mapping) else None
   263	    return _finite(value, "summary phase_energy_j.decode")
   264	
   265	
   266	def _sha256_file(path: Path, label: str) -> str:
   267	    try:
   268	        return _sha256(path.read_bytes())
   269	    except OSError as exc:
   270	        raise MintError(f"{label} cannot be read: {exc}") from exc
   271	
   272	
   273	def _path_independent_identifier(value: object, label: str) -> str:
   274	    if not isinstance(value, str) or not value:
   275	        raise MintError(f"{label} must be a nonempty string")
   276	    if value.startswith("/") or _WINDOWS_ABSOLUTE_RE.match(value):
   277	        name = PurePosixPath(value.replace("\\", "/")).name
   278	        if not name:
   279	            raise MintError(f"{label} cannot be reduced to a path-independent id")
   280	        return name
   281	    return value
   282	
   283	
   284	def _derive_stack_identity(
   285	    raw_config: Mapping[str, Any],
   286	    metadata: Mapping[str, Any],
   287	) -> Mapping[str, Any]:
   288	    """Derive the governed stack identity from current bundle evidence."""
   289	
   290	    hardware = raw_config.get("hardware_target")
   291	    workload = metadata.get("workload_provenance")
   292	    adapters = metadata.get("adapters")
   293	    runtime = adapters.get("runtime") if isinstance(adapters, Mapping) else None
   294	    telemetry = (
   295	        adapters.get("telemetry") if isinstance(adapters, Mapping) else None
   296	    )
   297	    prepare = (
   298	        runtime.get("prepare_metadata") if isinstance(runtime, Mapping) else None
   299	    )
   300	    model = workload.get("model") if isinstance(workload, Mapping) else None
   301	    artifact = (
   302	        model.get("artifact_identity") if isinstance(model, Mapping) else None
   303	    )
   304	    tokenizer = (
   305	        workload.get("tokenizer") if isinstance(workload, Mapping) else None
   306	    )
   307	    sampler = workload.get("sampler") if isinstance(workload, Mapping) else None
   308	    output_policy = (
   309	        workload.get("output_policy") if isinstance(workload, Mapping) else None
   310	    )
   311	    device = metadata.get("device")
   312	    quantization = metadata.get("quantization")
   313	    required_mappings = (
   314	        hardware,
   315	        workload,
   316	        runtime,
   317	        telemetry,
   318	        prepare,
   319	        artifact,
   320	        tokenizer,
   321	        sampler,
   322	        output_policy,
   323	        device,
   324	        quantization,
   325	    )
   326	    if not all(isinstance(value, Mapping) for value in required_mappings):
   327	        raise MintError("source stack identity fields are unavailable")
   328	    artifact_sha256 = artifact.get("sha256") or artifact.get("folded_sha256")
   329	    telemetry_name = telemetry.get("name")
   330	    if (
   331	        not isinstance(artifact_sha256, str)
   332	        or re.fullmatch(r"[0-9a-f]{64}", artifact_sha256) is None
   333	        or not isinstance(telemetry_name, str)
   334	        or not telemetry_name
   335	    ):
   336	        raise MintError("source stack artifact/telemetry identity is unavailable")
   337	    tokenizer_identity = dict(tokenizer)
   338	    tokenizer_identity["identifier"] = _path_independent_identifier(
   339	        tokenizer.get("identifier"), "tokenizer identifier"
   340	    )
   341	    runtime_version = (
   342	        prepare.get("version")
   343	        or prepare.get("mlx_version")
   344	        or prepare.get("mlx_lm_version")
   345	    )
   346	    if not isinstance(runtime_version, str) or not runtime_version:
   347	        raise MintError("source runtime version is unavailable")
   348	    return {
   349	        "hardware_unit": {
   350	            "config_id": hardware.get("id"),
   351	            "device": device.get("device"),
   352	            "machine": metadata.get("machine"),
   353	        },
   354	        "os_version": str(metadata.get("platform") or "unknown"),
   355	        "runtime_version": {
   356	            "name": runtime.get("name"),
   357	            "adapter": prepare.get("adapter"),
   358	            "version": runtime_version,
   359	        },
   360	        "kernel_library": str(
   361	            prepare.get("kernel_library") or "unavailable"
   362	        ),
   363	        "model_artifact_sha256": artifact_sha256,
   364	        "quantization": dict(quantization),
   365	        "tokenizer_identity": tokenizer_identity,
   366	        "sampler_output_policy": {
   367	            "sampler": dict(sampler),
   368	            "output_policy": {
   369	                key: output_policy.get(key)
   370	                for key in ("name", "requested_tokens", "stop_condition")
   371	            },
   372	        },
   373	        "batching_concurrency_policy": str(
   374	            prepare.get("batching_concurrency_policy")
   375	            or "single-request sequential"
   376	        ),
   377	        "measurement_boundary_label": {
   378	            "boundary": device.get("boundary", "unavailable"),
   379	            "rails": device.get("rail_manifest"),
   380	        },
   381	        "telemetry_backend": telemetry_name,
   382	    }
   383	
   384	
   385	def _source_admissible_half_width(
   386	    summary: Mapping[str, Any], bundle_id: str
   387	) -> float:
   388	    envelopes = summary.get("energy_anchor_shift_envelopes")
   389	    envelope = (
   390	        envelopes.get("/phase_energy_j/decode")
   391	        if isinstance(envelopes, Mapping)
   392	        else None
   393	    )
   394	    if not isinstance(envelope, Mapping):
   395	        raise MintError(
   396	            f"{bundle_id}: decode anchor-shift envelope is unavailable"
   397	        )
   398	    point = _finite(envelope.get("point_j"), f"{bundle_id} anchor point")
   399	    lower = _finite(envelope.get("lower_j"), f"{bundle_id} anchor lower")
   400	    upper = _finite(envelope.get("upper_j"), f"{bundle_id} anchor upper")
   401	    max_delta = _finite(
   402	        envelope.get("max_abs_delta_j"),
   403	        f"{bundle_id} anchor max delta",
   404	        nonnegative=True,
   405	    )
   406	    if lower > point or upper < point:
   407	        raise MintError(f"{bundle_id}: anchor-shift envelope does not contain point")
   408	    bound_terms = summary.get("energy_bound_terms_j")
   409	    interpolation = (
   410	        bound_terms.get("E_interpolation_joint_edge_bound_j")
   411	        if isinstance(bound_terms, Mapping)
   412	        else None
   413	    )
   414	    interpolation_j = _finite(
   415	        interpolation,
   416	        f"{bundle_id} joint interpolation bound",
   417	        nonnegative=True,
   418	    )
   419	    return max(point - lower, upper - point, max_delta) + interpolation_j
   420	
   421	
   422	def _strict_bundle(
   423	    root: Path,
   424	    bundle_id: object,
   425	    stored_row: Mapping[str, Any],
   426	    strict_validator: StrictValidator,
   427	    *,
   428	    operative_summary: Mapping[str, Any] | None = None,
   429	) -> AuthenticatedMember:
   430	    if (
   431	        not isinstance(bundle_id, str)
   432	        or not bundle_id
   433	        or "\\" in bundle_id
   434	        or PurePosixPath(bundle_id).name != bundle_id
   435	        or bundle_id in {".", ".."}
   436	    ):
   437	        raise MintError("bundle_id must be a safe basename")
   438	    resolved_root = root.resolve()
   439	    bundle_path = (root / bundle_id).resolve()
   440	    try:
   441	        bundle_path.relative_to(resolved_root)
   442	    except ValueError as exc:
   443	        raise MintError(f"{bundle_id}: bundle path escapes its evidence root") from exc
   444	    try:
   445	        problems = tuple(strict_validator(bundle_path, True))
   446	    except Exception as exc:
   447	        raise MintError(
   448	            f"{bundle_id}: strict validation raised {type(exc).__name__}: {exc}"
   449	        ) from exc
   450	    if problems:
   451	        raise MintError(f"{bundle_id}: strict validation failed: {problems[0]}")
   452	    config, _ = _load_json_object(bundle_path / "config.json", f"{bundle_id} config")
   453	    metadata, _ = _load_json_object(
   454	        bundle_path / "metadata.json", f"{bundle_id} metadata"
   455	    )
   456	    stored_summary, _ = _load_json_object(
   457	        bundle_path / "summary_metrics.json", f"{bundle_id} summary"
   458	    )
   459	    summary = (
   460	        operative_summary
   461	        if isinstance(operative_summary, Mapping)
   462	        else stored_summary
   463	    )
   464	    if summary.get("status") != "succeeded":
   465	        raise MintError(f"{bundle_id}: source summary status is not succeeded")
   466	    try:
   467	        bundle_sha256 = complete_bundle_sha256(bundle_path)
   468	    except ValueError as exc:
   469	        raise MintError(f"{bundle_id}: cannot hash complete bundle: {exc}") from exc
   470	    config_sha256 = _sha256_file(bundle_path / "config.json", f"{bundle_id} config")
   471	    if bundle_sha256 != stored_row.get("bundle_sha256"):
   472	        raise MintError(f"{bundle_id}: report bundle_sha256 does not match source bytes")
   473	    if config_sha256 != stored_row.get("config_sha256"):
   474	        raise MintError(f"{bundle_id}: report config_sha256 does not match source bytes")
   475	    metric = _metric_value(summary)
   476	    stored_metric = _finite(
   477	        stored_row.get("metric_value_j"), f"{bundle_id} report metric"
   478	    )
   479	    if not math.isclose(metric, stored_metric, rel_tol=1e-12, abs_tol=1e-12):
   480	        raise MintError(f"{bundle_id}: report metric does not match source bytes")
   481	    admissible_half_width = _source_admissible_half_width(summary, bundle_id)
   482	    if "anchor_shift_bound_j" in stored_row:
   483	        stored_width = _finite(
   484	            stored_row.get("anchor_shift_bound_j"),
   485	            f"{bundle_id} report anchor width",
   486	            nonnegative=True,
   487	        )
   488	        if not math.isclose(
   489	            admissible_half_width,
   490	            stored_width,
   491	            rel_tol=1e-12,
   492	            abs_tol=1e-12,
   493	        ):
   494	            raise MintError(
   495	                f"{bundle_id}: report anchor width does not match source bytes"
   496	            )
   497	    return AuthenticatedMember(
   498	        bundle_id=bundle_id,
   499	        bundle_sha256=bundle_sha256,
   500	        config_sha256=config_sha256,
   501	        metric_value_j=metric,
   502	        raw_config=config,
   503	        metadata=metadata,
   504	        summary=summary,
   505	        admissible_half_width_j=admissible_half_width,
   506	    )
   507	
   508	
   509	def _authenticated_consumption_summaries(
   510	    runs_root: Path,
   511	    referenced_bundle_ids: set[str],
   512	    evaluation_basis_sha256: str,
   513	    *,
   514	    target_bundle_ids: set[str],
   515	    consumption_semantics_id: str | None = None,
   516	    calibration_ledger_snapshot: CalibrationLedgerSnapshot | None = None,
   517	) -> tuple[Mapping[str, Mapping[str, Any]], str]:
   518	    """Replay the authenticated whole-window consumption semantics once."""
   519	
   520	    session = AuthenticatedConsumptionSession(
   521	        runs_root,
   522	        referenced_bundle_ids,
   523	        evaluation_basis_sha256=evaluation_basis_sha256,
   524	        consumption_semantics_id=(
   525	            consumption_semantics_id or MAX_BRACKET_CONSUMPTION_SEMANTICS_ID
   526	        ),
   527	        calibration_ledger_snapshot=calibration_ledger_snapshot,
   528	    )
   529	    reasons = whole_window_refusal_reasons(
   530	        runs_root,
   531	        referenced_bundle_ids,
   532	        evaluation_basis_sha256=evaluation_basis_sha256,
   533	        consumption_session=session,
   534	        consumption_semantics_id=consumption_semantics_id,
   535	    )
   536	    if reasons:
   537	        raise MintError(
   538	            "authenticated whole-window consumption refused: " + reasons[0]
   539	        )
   540	    if session.ready:
   541	        for bundle_id in sorted(target_bundle_ids):
   542	            target_reasons = session.path_refusal_reasons.get(
   543	                bundle_id, {}
   544	            ).get(TARGET_PRECHECK_PATH, ())
   545	            if target_reasons:
   546	                raise MintError(
   547	                    f"{bundle_id}: authenticated target metric refused: "
   548	                    f"{target_reasons[0]}"
   549	                )
   550	        summaries = {
   551	            bundle_id: summary
   552	            for bundle_id in referenced_bundle_ids
   553	            if isinstance(
   554	                (summary := session.summary_for(bundle_id)),
   555	                Mapping,
   556	            )
   557	        }
   558	        if set(summaries) != referenced_bundle_ids:
   559	            raise MintError(
   560	                "authenticated whole-window consumption omitted source members"
   561	            )
   562	        return summaries, getattr(
   563	            session,
   564	            "consumption_semantics_id",
   565	            consumption_semantics_id or MAX_BRACKET_CONSUMPTION_SEMANTICS_ID,
   566	        )
   567	
   568	    summaries: dict[str, Mapping[str, Any]] = {}
   569	    for bundle_id in referenced_bundle_ids:
   570	        summary, _ = _load_json_object(
   571	            runs_root / bundle_id / "summary_metrics.json",
   572	            f"{bundle_id} summary",
   573	        )
   574	        summaries[bundle_id] = summary
   575	    return summaries, MINTED_CONSUMPTION_SEMANTICS_ID
   576	
   577	
   578	def _spec_member_ids(spec: Mapping[str, Any]) -> list[str]:
   579	    ids: list[str] = []
   580	    for cell in spec.get("cells", []):
   581	        if not isinstance(cell, Mapping):
   582	            continue
   583	        members = cell.get("members")
   584	        if isinstance(members, list):
   585	            ids.extend(
   586	                row["bundle_id"]
   587	                for row in members
   588	                if isinstance(row, Mapping) and isinstance(row.get("bundle_id"), str)
   589	            )
   590	        blocks = cell.get("blocks")
   591	        if isinstance(blocks, list):
   592	            for block in blocks:
   593	                block_members = (
   594	                    block.get("members") if isinstance(block, Mapping) else None
   595	                )
   596	                if isinstance(block_members, Mapping):
   597	                    ids.extend(
   598	                        block_members[position]
   599	                        for position in _ABBA_POSITIONS
   600	                        if isinstance(block_members.get(position), str)
   601	                    )
   602	    return ids
   603	
   604	
   605	def _target_spec_cell(
   606	    spec: Mapping[str, Any], cell_id: str, kind: str
   607	) -> Mapping[str, Any]:
   608	    matches = [
   609	        cell
   610	        for cell in spec.get("cells", [])
   611	        if isinstance(cell, Mapping) and cell.get("cell_id") == cell_id
   612	    ]
   613	    if len(matches) != 1:
   614	        raise MintError(f"extraction spec must contain exactly one {cell_id!r} cell")
   615	    cell = matches[0]
   616	    if (
   617	        cell.get("kind") != kind
   618	        or cell.get("metric") != METRIC
   619	        or cell.get("window_class") != WINDOW_CLASS
   620	    ):
   620	    ):
   621	        raise MintError(f"{cell_id}: extraction spec cell key/kind mismatch")
   622	    return cell
   623	
   624	
   625	def _target_report_cell(
   626	    report: Mapping[str, Any], cell_id: str, kind: str
   627	) -> Mapping[str, Any]:
   628	    matches = [
   629	        cell
   630	        for cell in report.get("cells", [])
   631	        if isinstance(cell, Mapping) and cell.get("cell_id") == cell_id
   632	    ]
   633	    if len(matches) != 1:
   634	        raise MintError(f"extraction report must contain exactly one {cell_id!r} cell")
   635	    cell = matches[0]
   636	    if (
   637	        cell.get("kind") != kind
   638	        or cell.get("metric") != METRIC
   639	        or cell.get("window_class") != WINDOW_CLASS
   640	        or cell.get("extractable") is not True
   641	        or cell.get("refusal_reasons") not in ([], ())
   642	    ):
   643	        raise MintError(f"{cell_id}: extraction report is not an extractable target")
   644	    floor = cell.get("floor")
   645	    if not isinstance(floor, Mapping):
   646	        raise MintError(f"{cell_id}: extraction report has no floor row")
   647	    return cell
   648	
   649	
   650	def _report_members(
   651	    cell: Mapping[str, Any], spec_cell: Mapping[str, Any], kind: str
   652	) -> tuple[list[Mapping[str, Any]], tuple[float, ...]]:
   653	    raw_members = cell.get("members")
   654	    if not isinstance(raw_members, list) or not all(
   655	        isinstance(row, Mapping) for row in raw_members
   656	    ):
   657	        raise MintError("extraction report members must be an array of objects")
   658	    members = [
   659	        row
   660	        for row in raw_members
   661	        if row.get("excluded") is False and not row.get("reasons")
   662	    ]
   663	    if len(members) != len(raw_members):
   664	        raise MintError("target extraction cell contains excluded or refused members")
   665	    by_id = {row.get("bundle_id"): row for row in members}
   666	    if len(by_id) != len(members) or None in by_id:
   667	        raise MintError("target extraction report has duplicate/invalid bundle ids")
   668	    if kind == "absolute":
   669	        spec_members = spec_cell.get("members")
   670	        if not isinstance(spec_members, list):
   671	            raise MintError("absolute extraction spec members must be an array")
   672	        ids = [
   673	            row.get("bundle_id") if isinstance(row, Mapping) else None
   674	            for row in spec_members
   675	        ]
   676	        if ids != [row.get("bundle_id") for row in members]:
   677	            raise MintError("absolute report membership/order differs from extraction spec")
   678	        widths = tuple(
   679	            _finite(
   680	                row.get("anchor_shift_bound_j"),
   681	                f"{row.get('bundle_id')} anchor width",
   682	                nonnegative=True,
   683	            )
   684	            for row in members
   685	        )
   686	        return members, widths
   687	
   688	    blocks = spec_cell.get("blocks")
   689	    if not isinstance(blocks, list):
   690	        raise MintError("comparative extraction spec blocks must be an array")
   691	    ordered: list[Mapping[str, Any]] = []
   692	    widths: list[float] = []
   693	    for block in blocks:
   694	        if not isinstance(block, Mapping):
   695	            raise MintError("comparative extraction spec block must be an object")
   696	        block_id = block.get("block_id")
   697	        spec_members = block.get("members")
   698	        if not isinstance(spec_members, Mapping):
   699	            raise MintError("comparative block members must be an object")
   700	        block_rows: list[Mapping[str, Any]] = []
   701	        for position in _ABBA_POSITIONS:
   702	            bundle_id = spec_members.get(position)
   703	            row = by_id.get(bundle_id)
   704	            if (
   705	                not isinstance(row, Mapping)
   706	                or row.get("block_id") != block_id
   707	                or row.get("position") != position
   708	            ):
   709	                raise MintError(
   710	                    "comparative report membership/order differs from extraction spec"
   711	                )
   712	            block_rows.append(row)
   713	        ordered.extend(block_rows)
   714	        widths.append(
   715	            math.fsum(
   716	                _finite(
   717	                    row.get("anchor_shift_bound_j"),
   718	                    f"{row.get('bundle_id')} anchor width",
   719	                    nonnegative=True,
   720	                )
   721	                for row in block_rows
   722	            )
   723	            / 2.0
   724	        )
   725	    if ordered != members:
   726	        raise MintError("comparative report member sequence is not flattened A1/B1/B2/A2")
   727	    return ordered, tuple(widths)
   728	
   729	
   730	def _verify_report_widths(
   731	    cell: Mapping[str, Any], widths: Sequence[float]
   732	) -> None:
   733	    floor = cell.get("floor")
   734	    report_widths = (
   735	        floor.get("admissible_half_widths_j")
   736	        if isinstance(floor, Mapping)
   737	        else None
   738	    )
   739	    if (
   740	        not isinstance(report_widths, list)
   741	        or len(report_widths) != len(widths)
   742	        or any(
   743	            not math.isclose(
   744	                _finite(value, "reported admissible width", nonnegative=True),
   745	                expected,
   746	                rel_tol=0.0,
   747	                abs_tol=0.0,
   748	            )
   749	            for value, expected in zip(report_widths, widths)
   750	        )
   751	    ):
   752	        raise MintError(
   753	            "extraction-report widths differ element-for-element from member evidence"
   754	        )
   755	
   756	
   757	def _evaluation_basis_members(
   758	    rows: Sequence[Mapping[str, Any]], expected_sha256: str
   759	) -> frozenset[str]:
   760	    member_sets: list[frozenset[str]] = []
   761	    for row in rows:
   762	        basis = row.get("evaluation_basis")
   763	        if not isinstance(basis, Mapping) or basis.get("sha256") != expected_sha256:
   764	            continue
   765	        occurrences = basis.get("member_occurrences")
   766	        if not isinstance(occurrences, list) or any(
   767	            not isinstance(item, Mapping)
   768	            or not isinstance(item.get("bundle_id"), str)
   769	            for item in occurrences
   770	        ):
   771	            raise MintError("evaluation basis member_occurrences are malformed")
   772	        member_ids = [item["bundle_id"] for item in occurrences]
   773	        if len(member_ids) != len(set(member_ids)):
   774	            raise MintError("evaluation basis contains duplicate member occurrences")
   775	        member_sets.append(frozenset(member_ids))
   776	    if len(member_sets) != 1:
   777	        raise MintError(
   778	            f"campaign log must contain exactly one evaluation basis {expected_sha256}"
   779	        )
   780	    return member_sets[0]
   781	
   782	
   783	def _order_manifest_ids(order_manifest: Mapping[str, Any]) -> list[str]:
   784	    rows = order_manifest.get("executed_order")
   785	    if not isinstance(rows, list):
   786	        raise MintError("order manifest executed_order must be an array")
   787	    ids: list[str] = []
   788	    for row in rows:
   789	        if not isinstance(row, Mapping):
   790	            raise MintError("order manifest rows must be objects")
   791	        bundle_id = row.get("run_id")
   792	        if not isinstance(bundle_id, str) or not bundle_id:
   793	            raise MintError("order manifest row run_id must be nonempty")
   794	        ids.append(bundle_id)
   795	    if len(ids) != len(set(ids)):
   796	        raise MintError("order manifest executed_order contains duplicate run ids")
   797	    return ids
   798	
   799	
   800	def _validate_order(
   801	    order_manifest: Mapping[str, Any],
   802	    *,
   803	    target_ids: Sequence[str],
   804	    spec_ids: Sequence[str],
   805	) -> None:
   806	    ordered = _order_manifest_ids(order_manifest)
   807	    if set(ordered) != set(spec_ids) or len(ordered) != len(spec_ids):
   808	        raise MintError("order manifest membership differs from extraction spec")
   809	    selected = [bundle_id for bundle_id in ordered if bundle_id in set(target_ids)]
   810	    if selected != list(target_ids):
   811	        raise MintError("order manifest disagrees with target component member order")
   812	
   813	
   814	def _source_regime(
   815	    members: Sequence[AuthenticatedMember],
   816	) -> tuple[Mapping[str, Any], str, str]:
   817	    if not members:
   818	        raise MintError("component needs authenticated source members")
   819	    stack_identities: list[Mapping[str, Any]] = []
   820	    scientific_hashes: set[str] = set()
   821	    backends: set[str] = set()
   822	    for member in members:
   823	        stack = _derive_stack_identity(member.raw_config, member.metadata)
   824	        stack_identities.append(stack)
   825	        scientific = scientific_config_identity(member.raw_config)
   826	        if not isinstance(scientific, Mapping):
   827	            raise MintError(
   828	                f"{member.bundle_id}: scientific config identity is unavailable"
   829	            )
   830	        scientific_hashes.add(
   831	            _sha256(
   832	                json.dumps(
   833	                    scientific,
   834	                    sort_keys=True,
   835	                    separators=(",", ":"),
   836	                    allow_nan=False,
   837	                ).encode("utf-8")
   838	            )
   839	        )
   840	        hardware = member.raw_config.get("hardware_target")
   841	        backend = (
   842	            hardware.get("telemetry_backend")
   843	            if isinstance(hardware, Mapping)
   844	            else None
   845	        )
   846	        if not isinstance(backend, str) or not backend:
   847	            raise MintError(f"{member.bundle_id}: telemetry backend is unavailable")
   848	        backends.add(backend)
   849	    stack_hashes = {
   850	        canonical_domain_sha256(STACK_IDENTITY_DOMAIN, stack)
   851	        for stack in stack_identities
   852	    }
   853	    if len(stack_hashes) != 1:
   854	        raise MintError("component members do not share one stack identity")
   855	    if len(scientific_hashes) != 1:
   856	        raise MintError("component members do not share one scientific config identity")
   857	    if len(backends) != 1:
   858	        raise MintError("component members do not share one telemetry backend")
   859	    stress = _stress_observed(members)
   860	    stack = dict(stack_identities[0])
   861	    return (
   862	        {
   863	            "stack_identity": stack,
   864	            "stack_identity_sha256": next(iter(stack_hashes)),
   865	            "stress_observed": stress,
   866	        },
   867	        next(iter(scientific_hashes)),
   868	        next(iter(backends)),
   869	    )
   870	
   871	
   872	def _stress_observed(
   873	    members: Sequence[AuthenticatedMember],
   874	) -> Mapping[str, Any]:
   875	    powers: list[float] = []
   876	    durations: list[float] = []
   877	    p95_gaps: list[float] = []
   878	    bracketing_gaps: list[float] = []
   879	    cadence_ratios: list[float] = []
   880	    clock_bounds: list[float] = []
   881	    interpolation_bounds: list[float] = []
   882	
   883	    for member in members:
   884	        prechecks = member.summary.get("window_evidence_precheck")
   885	        phases = prechecks.get("phase") if isinstance(prechecks, Mapping) else None
   886	        decode = phases.get("decode") if isinstance(phases, Mapping) else None
   887	        windows = decode.get("windows") if isinstance(decode, Mapping) else None
   888	        if not isinstance(windows, list) or not windows:
   889	            raise MintError(
   890	                f"{member.bundle_id}: phase decode stress evidence is unavailable"
   891	            )
   892	        member_duration = 0.0
   893	        for window in windows:
   894	            if not isinstance(window, Mapping):
   895	                raise MintError(f"{member.bundle_id}: malformed decode stress window")
   896	            duration = _finite(
   897	                window.get("window_duration_s"),
   898	                f"{member.bundle_id} window duration",
   899	                nonnegative=True,
   900	            )
   901	            p95 = _finite(
   902	                window.get("observed_window_p95_sample_gap_s"),
   903	                f"{member.bundle_id} p95 gap",
   904	                nonnegative=True,
   905	            )
   906	            bracket = _finite(
   907	                window.get("observed_bracketing_max_sample_gap_s"),
   908	                f"{member.bundle_id} bracketing gap",
   909	                nonnegative=True,
   910	            )
   911	            cadence = _finite(
   912	                window.get("cadence_ratio"),
   913	                f"{member.bundle_id} cadence ratio",
   914	                nonnegative=True,
   915	            )
   916	            clock = _finite(
   917	                window.get("clock_anchor_bound_s"),
   918	                f"{member.bundle_id} clock anchor bound",
   919	                nonnegative=True,
   920	            )
   921	            interpolation = _finite(
   922	                window.get("interpolation_joint_edge_bound_j"),
   923	                f"{member.bundle_id} interpolation bound",
   924	                nonnegative=True,
   925	            )
   926	            if duration <= 0.0:
   927	                raise MintError(f"{member.bundle_id}: window duration must be positive")
   928	            member_duration += duration
   929	            durations.append(duration)
   930	            p95_gaps.append(p95)
   931	            bracketing_gaps.append(bracket)
   932	            cadence_ratios.append(cadence)
   933	            clock_bounds.append(clock)
   934	            interpolation_bounds.append(interpolation)
   935	        powers.append(member.metric_value_j / member_duration)
   936	
   937	    return {
   938	        "mean_power_w_min": min(powers),
   939	        "mean_power_w_max": max(powers),
   940	        "window_duration_s_min": min(durations),
   941	        "window_duration_s_max": max(durations),
   942	        "p95_sample_gap_s_max": max(p95_gaps),
   943	        "bracketing_sample_gap_s_max": max(bracketing_gaps),
   944	        "cadence_ratio_min": min(cadence_ratios),
   945	        "bound_terms": {
   946	            "clock_anchor_bound_s": {
   947	                "applicability": "required",
   948	                "maximum": max(clock_bounds),
   949	            },
   950	            "interpolation_bound_j": {
   951	                "applicability": "required",
   952	                "maximum": max(interpolation_bounds),
   953	            },
   954	            "idle_drift_bound_j": {
   955	                "applicability": "not_applicable",
   956	                "maximum": None,
   957	            },
   958	        },
   959	    }
   960	
   961	
   962	def _tag_value(raw_config: Mapping[str, Any], prefix: str) -> str | None:
   963	    run_metadata = raw_config.get("run_metadata")
   964	    tags = (
   965	        run_metadata.get("tags")
   966	        if isinstance(run_metadata, Mapping)
   967	        else None
   968	    )
   969	    if not isinstance(tags, list) or any(not isinstance(tag, str) for tag in tags):
   970	        return None
   971	    values = [tag[len(prefix) :] for tag in tags if tag.startswith(prefix)]
   972	    return values[0] if len(values) == 1 and values[0] else None
   973	
   974	
   975	def _verify_source_order_tags(
   976	    member: AuthenticatedMember,
   977	    report_row: Mapping[str, Any],
   978	    *,
   979	    comparative: bool,
   980	) -> None:
   981	    if _tag_value(
   982	        member.raw_config, "calibration-plan-sha256="
   983	    ) != PLAN_SHA256:
   984	        raise MintError(f"{member.bundle_id}: source calibration-plan tag mismatch")
   985	    if not comparative:
   986	        return
   987	    if _tag_value(
   988	        member.raw_config, "calibration-abba-block-id="
   989	    ) != report_row.get("block_id"):
   990	        raise MintError(f"{member.bundle_id}: source ABBA block tag mismatch")
   991	    position = report_row.get("position")
   992	    expected_label = (
   993	        position[0]
   994	        if isinstance(position, str) and position in _ABBA_POSITIONS
   995	        else None
   996	    )
   997	    if _tag_value(
   998	        member.raw_config, "calibration-abba-label="
   999	    ) != expected_label:
  1000	        raise MintError(f"{member.bundle_id}: source ABBA label tag mismatch")
  1001	    expected_index = (
  1002	        str(_ABBA_POSITIONS.index(position) + 1)
  1003	        if position in _ABBA_POSITIONS
  1004	        else None
  1005	    )
  1006	    if _tag_value(
  1007	        member.raw_config, "calibration-abba-sequence-index="
  1008	    ) != expected_index:
  1009	        raise MintError(f"{member.bundle_id}: source ABBA sequence tag mismatch")
  1010	
  1011	
  1012	def _authenticate_component(
  1013	    paths: ComponentPaths,
  1014	    *,
  1015	    expected_cell_id: str,
  1016	    expected_basis_sha256: str,
  1017	    strict_validator: StrictValidator,
  1018	    consumption_authenticator: ConsumptionAuthenticator = (
  1019	        _authenticated_consumption_summaries
  1020	    ),
  1021	    allowance_deriver: AllowanceDeriver = whole_window_drift_allowances,
  1022	    expected_consumption_semantics_id: str | None = None,
  1023	    calibration_ledger_snapshot: CalibrationLedgerSnapshot | None = None,
  1024	) -> AuthenticatedComponent:
  1025	    if calibration_ledger_snapshot is None:
  1026	        acceptance = load_calibration_acceptance_bound()
  1027	        cutoff = (
  1028	            acceptance.get("ledger_cutoff")
  1029	            if isinstance(acceptance, Mapping)
  1030	            else None
  1031	        )
  1032	        calibration_ledger_snapshot = load_calibration_ledger_snapshot(
  1033	            baseline_sequence=(
  1034	                cutoff.get("sequence") if isinstance(cutoff, Mapping) else None
  1035	            ),
  1036	            baseline_digest=(
  1037	                cutoff.get("head_digest") if isinstance(cutoff, Mapping) else None
  1038	            ),
  1039	        )
  1040	    report, report_raw = _load_json_object(paths.report_path, "extraction report")

exec
/bin/zsh -lc "nl -ba scripts/mint_floor_artifact.py | sed -n '1010,1240p'; nl -ba joulewise/calibration_ledger.py | sed -n '140,240p'; nl -ba joulewise/calibration_ledger.py | sed -n '380,740p'; nl -ba joulewise/calibration_bracketing.py | sed -n '400,520p'" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u3
 succeeded in 0ms:
  1010	
  1011	
  1012	def _authenticate_component(
  1013	    paths: ComponentPaths,
  1014	    *,
  1015	    expected_cell_id: str,
  1016	    expected_basis_sha256: str,
  1017	    strict_validator: StrictValidator,
  1018	    consumption_authenticator: ConsumptionAuthenticator = (
  1019	        _authenticated_consumption_summaries
  1020	    ),
  1021	    allowance_deriver: AllowanceDeriver = whole_window_drift_allowances,
  1022	    expected_consumption_semantics_id: str | None = None,
  1023	    calibration_ledger_snapshot: CalibrationLedgerSnapshot | None = None,
  1024	) -> AuthenticatedComponent:
  1025	    if calibration_ledger_snapshot is None:
  1026	        acceptance = load_calibration_acceptance_bound()
  1027	        cutoff = (
  1028	            acceptance.get("ledger_cutoff")
  1029	            if isinstance(acceptance, Mapping)
  1030	            else None
  1031	        )
  1032	        calibration_ledger_snapshot = load_calibration_ledger_snapshot(
  1033	            baseline_sequence=(
  1034	                cutoff.get("sequence") if isinstance(cutoff, Mapping) else None
  1035	            ),
  1036	            baseline_digest=(
  1037	                cutoff.get("head_digest") if isinstance(cutoff, Mapping) else None
  1038	            ),
  1039	        )
  1040	    report, report_raw = _load_json_object(paths.report_path, "extraction report")
  1041	    spec, spec_raw = _load_json_object(paths.spec_path, "extraction spec")
  1042	    if (
  1043	        report.get("schema_version") != EXTRACTION_SCHEMA_VERSION
  1044	        or report.get("spec_schema_version") != EXTRACTION_SPEC_SCHEMA_VERSION
  1045	    ):
  1046	        raise MintError("extraction report schema literals are not governed")
  1047	    if (
  1048	        report.get("spec_membership_refusals") not in ([], ())
  1049	        or report.get("idle_admission_refusals") not in ([], ())
  1050	    ):
  1051	        raise MintError("extraction report carries global refusal records")
  1052	    report_root = report.get("runs_root")
  1053	    if (
  1054	        not isinstance(report_root, str)
  1055	        or Path(report_root).resolve() != paths.evidence_root.resolve()
  1056	    ):
  1057	        raise MintError("extraction report runs_root differs from evidence root")
  1058	    errors = validate_extraction_spec(spec)
  1059	    if errors:
  1060	        raise MintError(f"invalid extraction spec: {errors[0]}")
  1061	    order, order_raw = _load_json_object(
  1062	        paths.order_manifest_path, "order manifest"
  1063	    )
  1064	    spec_cell = _target_spec_cell(spec, expected_cell_id, paths.expected_kind)
  1065	    cell = _target_report_cell(report, expected_cell_id, paths.expected_kind)
  1066	    report_members, widths = _report_members(cell, spec_cell, paths.expected_kind)
  1067	    _verify_report_widths(cell, widths)
  1068	    spec_ids = _spec_member_ids(spec)
  1069	    referenced_bundle_ids = set(spec_ids)
  1070	    target_ids = {
  1071	        row.get("bundle_id")
  1072	        for row in report_members
  1073	        if isinstance(row.get("bundle_id"), str)
  1074	    }
  1075	    semantics = report.get("consumption_semantics_id")
  1076	    if semantics not in _SEMANTICS_IDS:
  1077	        raise MintError("extraction report consumption_semantics_id is unknown")
  1078	    if (
  1079	        expected_consumption_semantics_id is not None
  1080	        and semantics != expected_consumption_semantics_id
  1081	    ):
  1082	        raise MintError(
  1083	            "extraction report consumption_semantics_id differs from explicit dispatch"
  1084	        )
  1085	    operative_summaries, actual_semantics = consumption_authenticator(
  1086	        paths.evidence_root,
  1087	        referenced_bundle_ids,
  1088	        expected_basis_sha256,
  1089	        target_bundle_ids=target_ids,
  1090	        consumption_semantics_id=expected_consumption_semantics_id,
  1091	        calibration_ledger_snapshot=calibration_ledger_snapshot,
  1092	    )
  1093	    if semantics != actual_semantics:
  1094	        raise MintError(
  1095	            "extraction report consumption_semantics_id differs from "
  1096	            "authenticated source consumption"
  1097	        )
  1098	    if not target_ids.issubset(operative_summaries):
  1099	        raise MintError("authenticated consumption omitted target report members")
  1100	    members = tuple(
  1101	        _strict_bundle(
  1102	            paths.evidence_root,
  1103	            row.get("bundle_id"),
  1104	            row,
  1105	            strict_validator,
  1106	            operative_summary=(
  1107	                operative_summaries.get(row.get("bundle_id"))
  1108	                if isinstance(row.get("bundle_id"), str)
  1109	                else None
  1110	            ),
  1111	        )
  1112	        for row in report_members
  1113	    )
  1114	    for member, report_row in zip(members, report_members, strict=True):
  1115	        _verify_source_order_tags(
  1116	            member,
  1117	            report_row,
  1118	            comparative=paths.expected_kind == "comparative",
  1119	        )
  1120	    _validate_order(
  1121	        order,
  1122	        target_ids=[member.bundle_id for member in members],
  1123	        spec_ids=spec_ids,
  1124	    )
  1125	    campaign_rows, campaign_raw = _load_json_lines(
  1126	        paths.evidence_root / "campaign_log.jsonl", "campaign log"
  1127	    )
  1128	    campaign_log_sha256 = _sha256(campaign_raw)
  1129	    basis_members = _evaluation_basis_members(
  1130	        campaign_rows, expected_basis_sha256
  1131	    )
  1132	    if not set(spec_ids).issubset(basis_members):
  1133	        raise MintError(
  1134	            "extraction-spec members are not a subset of the evaluation basis"
  1135	        )
  1136	    allowance = cell.get("whole_window_drift_allowance")
  1137	    if not isinstance(allowance, Mapping):
  1138	        raise MintError("target report cell has no whole-window drift allowance")
  1139	    basis_sha256 = allowance.get("whole_window_evaluation_basis_sha256")
  1140	    if basis_sha256 != expected_basis_sha256:
  1141	        raise MintError("component whole-window evaluation basis is not pinned")
  1142	    floor_basis = cell["floor"].get("whole_window_drift_allowance_provenance")
  1143	    if not isinstance(floor_basis, Mapping) or dict(floor_basis) != dict(allowance):
  1144	        raise MintError("floor allowance provenance differs from component allowance")
  1145	
  1146	    campaign_log_path = paths.evidence_root / "campaign_log.jsonl"
  1147	    try:
  1148	        allowance_session = AuthenticatedConsumptionSession(
  1149	            paths.evidence_root,
  1150	            referenced_bundle_ids,
  1151	            evaluation_basis_sha256=expected_basis_sha256,
  1152	            consumption_semantics_id=(
  1153	                expected_consumption_semantics_id
  1154	                or MAX_BRACKET_CONSUMPTION_SEMANTICS_ID
  1155	            ),
  1156	            calibration_ledger_snapshot=calibration_ledger_snapshot,
  1157	        )
  1158	        allowance_result = allowance_deriver(
  1159	            paths.evidence_root,
  1160	            referenced_bundle_ids,
  1161	            evaluation_basis_sha256=expected_basis_sha256,
  1162	            consumption_session=allowance_session,
  1163	            consumption_semantics_id=expected_consumption_semantics_id,
  1164	        )
  1165	    except Exception as exc:
  1166	        if (
  1167	            _sha256_file(campaign_log_path, "campaign log")
  1168	            != campaign_log_sha256
  1169	        ):
  1170	            raise MintError(
  1171	                "campaign log changed during whole-window allowance "
  1172	                "re-derivation"
  1173	            ) from exc
  1174	        raise MintError(
  1175	            "whole-window drift allowance is not derivable from "
  1176	            f"authenticated campaign evidence: {type(exc).__name__}: {exc}"
  1177	        ) from exc
  1178	    # The derivation re-reads campaign_log.jsonl. Re-pin the bytes afterward
  1179	    # so the authenticated input and the derivation input share one custody
  1180	    # identity even if the file was concurrently replaced.
  1181	    if _sha256_file(campaign_log_path, "campaign log") != campaign_log_sha256:
  1182	        raise MintError(
  1183	            "campaign log changed during whole-window allowance re-derivation"
  1184	        )
  1185	    if getattr(allowance_result, "status", None) != "allowances":
  1186	        raise MintError(
  1187	            "whole-window drift allowance is not derivable from "
  1188	            "authenticated campaign evidence "
  1189	            f"(status={getattr(allowance_result, 'status', None)!r})"
  1190	        )
  1191	    derived_allowances = getattr(allowance_result, "allowances", None)
  1192	    claim_family = neg8_claim_family_for_metric(METRIC)
  1193	    derived_allowance = (
  1194	        derived_allowances.get(claim_family)
  1195	        if isinstance(derived_allowances, Mapping)
  1196	        else None
  1197	    )
  1198	    if not isinstance(derived_allowance, Mapping):
  1199	        raise MintError(
  1200	            "authenticated whole-window drift allowance is missing "
  1201	            f"claim family {claim_family!r}"
  1202	        )
  1203	    # Both records are JSON-number mappings parsed by Python. Exact nested
  1204	    # equality enforces the contract's "differs in any way" rule, including
  1205	    # sub-microjoule substitutions and non-numeric provenance changes.
  1206	    if dict(derived_allowance) != dict(allowance):
  1207	        raise MintError(
  1208	            "report whole-window drift allowance differs from "
  1209	            "authenticated source re-derivation"
  1210	        )
  1211	
  1212	    regime, scientific_hash, backend = _source_regime(members)
  1213	    return AuthenticatedComponent(
  1214	        evidence_root_id=paths.evidence_root_id,
  1215	        calibration_cell_id=paths.calibration_cell_id,
  1216	        kind=paths.expected_kind,
  1217	        report=report,
  1218	        report_sha256=_sha256(report_raw),
  1219	        spec=spec,
  1220	        spec_sha256=_sha256(spec_raw),
  1221	        order_manifest=order,
  1222	        order_manifest_sha256=_sha256(order_raw),
  1223	        campaign_log_sha256=campaign_log_sha256,
  1224	        cell=cell,
  1225	        spec_cell=spec_cell,
  1226	        members=members,
  1227	        widths_j=widths,
  1228	        whole_window_evaluation_basis_sha256=basis_sha256,
  1229	        evaluation_basis_member_count=len(basis_members),
  1230	        consumption_semantics_id=semantics,
  1231	        whole_window_drift_allowance=dict(allowance),
  1232	        source_regime=regime,
  1233	        scientific_config_identity_sha256=scientific_hash,
  1234	        backend=backend,
  1235	    )
  1236	
  1237	
  1238	def _definition_binding(component: AuthenticatedComponent) -> Mapping[str, Any]:
  1239	    bindings = component.spec_cell.get("condition_family_definitions")
  1240	    if not isinstance(bindings, Mapping):
   140	
   141	def _is_sha256(value: object) -> bool:
   142	    return isinstance(value, str) and _SHA256_RE.fullmatch(value) is not None
   143	
   144	
   145	def _normalized_vector(
   146	    value: Mapping[str, Any] | None,
   147	    fields: Sequence[str],
   148	) -> dict[str, Any]:
   149	    source = value if isinstance(value, Mapping) else {}
   150	    return {field: source.get(field) for field in fields}
   151	
   152	
   153	def content_id_from_artifact_hashes(artifact_sha256: Mapping[str, Any]) -> str | None:
   154	    """Return the path-independent identity of canonical primary bytes.
   155	
   156	    The authenticated evidence document and its manifest are the canonical
   157	    byte pair.  A copied custody tree therefore retains the same identity.
   158	    Other receipt hashes remain custody checks but do not manufacture a new
   159	    observation when a derived representation is regenerated.
   160	    """
   161	
   162	    identity = {
   163	        name: artifact_sha256.get(name) for name in CONTENT_ID_ARTIFACTS
   164	    }
   165	    if any(not _is_sha256(value) for value in identity.values()):
   166	        return None
   167	    return canonical_sha256(identity)
   168	
   169	
   170	def artifact_hashes(custody_dir: Path) -> dict[str, str]:
   171	    """Hash every governed artifact present in one finalized custody tree."""
   172	
   173	    root = Path(custody_dir)
   174	    result: dict[str, str] = {}
   175	    for relative in GOVERNED_ARTIFACTS:
   176	        path = root / relative
   177	        if path.is_file():
   178	            result[relative] = hashlib.sha256(path.read_bytes()).hexdigest()
   179	    return result
   180	
   181	
   182	def receipt_core(receipt: Mapping[str, Any]) -> dict[str, Any]:
   183	    return {key: value for key, value in receipt.items() if key != "receipt_digest"}
   184	
   185	
   186	def _receipt_digest(receipt: Mapping[str, Any]) -> str:
   187	    return canonical_sha256(receipt_core(receipt))
   188	
   189	
   190	@dataclass(frozen=True)
   191	class LedgerObservation:
   192	    sequence: int
   193	    receipt_digest: str
   194	    attempt_id: str
   195	    content_id: str | None
   196	    artifact_sha256: Mapping[str, str]
   197	    identity_epoch: Mapping[str, Any]
   198	    t1_bindings: Mapping[str, Any]
   199	    capture_wall_time_s: str | None
   200	    exact_bound_lexeme_s: str | None
   201	    disposition: str
   202	    custody_locator: str
   203	    observation_kind: str = "live-capture"
   204	
   205	    @property
   206	    def classification_disposition(self) -> str:
   207	        """Map the writer terminal state onto the R2 observation schema."""
   208	
   209	        return (
   210	            "unresolved" if self.disposition == "abandoned" else self.disposition
   211	        )
   212	
   213	    @property
   214	    def is_historical_import(self) -> bool:
   215	        return self.observation_kind == "historical-import"
   216	
   217	
   218	@dataclass(frozen=True)
   219	class CalibrationLedgerSnapshot:
   220	    """One immutable, fully checked view threaded through an evaluation."""
   221	
   222	    ledger_schema: str
   223	    ledger_path: Path
   224	    head_sequence: int
   225	    head_digest: str
   226	    receipts: tuple[Mapping[str, Any], ...]
   227	    observations: tuple[LedgerObservation, ...]
   228	    refusal_reasons: tuple[str, ...]
   229	    baseline_sequence: int | None = None
   230	    baseline_digest: str | None = None
   231	
   232	    @property
   233	    def valid(self) -> bool:
   234	        return not self.refusal_reasons
   235	
   236	    @property
   237	    def observation_by_attempt(self) -> Mapping[str, LedgerObservation]:
   238	        return MappingProxyType(
   239	            {observation.attempt_id: observation for observation in self.observations}
   240	        )
   380	        or isinstance(sequence, bool)
   381	        or not isinstance(sequence, int)
   382	        or sequence < 1
   383	        or not _is_sha256(receipt.get("predecessor_digest"))
   384	        or event
   385	        not in {
   386	            "reservation",
   387	            "finalization",
   388	            HISTORICAL_IMPORT_RESERVATION_EVENT,
   389	            HISTORICAL_IMPORT_FINALIZATION_EVENT,
   390	        }
   391	        or not isinstance(receipt.get("attempt_id"), str)
   392	        or not receipt.get("attempt_id")
   393	        or disposition not in ALL_DISPOSITIONS
   394	        or not isinstance(receipt.get("custody_locator"), str)
   395	        or not isinstance(artifacts, Mapping)
   396	        or any(
   397	            not isinstance(name, str) or not name or not _is_sha256(digest)
   398	            for name, digest in artifacts.items()
   399	        )
   400	        or not isinstance(epoch, Mapping)
   401	        or set(epoch) != set(IDENTITY_EPOCH_FIELDS)
   402	        or not isinstance(t1, Mapping)
   403	        or set(t1) != set(T1_FIELDS)
   404	        or (capture is not None and not isinstance(capture, str))
   405	        or (bound is not None and not isinstance(bound, str))
   406	        or not _is_sha256(receipt.get("receipt_digest"))
   407	        or receipt.get("receipt_digest") != _receipt_digest(receipt)
   408	    ):
   409	        return False
   410	    content_id = receipt.get("content_id")
   411	    if content_id is not None and not _is_sha256(content_id):
   412	        return False
   413	    if event in {"reservation", HISTORICAL_IMPORT_RESERVATION_EVENT}:
   414	        historical_input_sha256 = receipt.get(
   415	            _HISTORICAL_IMPORT_INPUT_SHA256_KEY
   416	        )
   417	        return (
   418	            disposition == "pending"
   419	            and content_id is None
   420	            and not artifacts
   421	            and capture is None
   422	            and bound is None
   423	            and all(
   424	                epoch.get(field) not in (None, "")
   425	                for field in IDENTITY_EPOCH_FIELDS
   426	            )
   427	            and all(t1.get(field) not in (None, "") for field in T1_FIELDS)
   428	            and (
   429	                event != HISTORICAL_IMPORT_RESERVATION_EVENT
   430	                or isinstance(historical_input_sha256, Mapping)
   431	                and set(historical_input_sha256)
   432	                == _HISTORICAL_IMPORT_INPUT_SHA256_KEYS
   433	                and all(
   434	                    _is_sha256(historical_input_sha256.get(name))
   435	                    for name in _HISTORICAL_IMPORT_INPUT_SHA256_KEYS
   436	                )
   437	            )
   438	        )
   439	    if disposition not in FINAL_DISPOSITIONS:
   440	        return False
   441	    if disposition == "abandoned":
   442	        # R1 retains the terminal writer state as ``abandoned`` while R2
   443	        # classifies it as unresolved.  When canonical primary bytes exist,
   444	        # preserve their authentic content identity; a partial/no-content
   445	        # attempt remains representable with a null content id.
   446	        return content_id == content_id_from_artifact_hashes(artifacts)
   447	    if (
   448	        content_id is None
   449	        or content_id_from_artifact_hashes(artifacts) != content_id
   450	        or not receipt.get("custody_locator")
   451	        or any(epoch.get(field) in (None, "") for field in IDENTITY_EPOCH_FIELDS)
   452	        or any(t1.get(field) in (None, "") for field in T1_FIELDS)
   453	        or capture is None
   454	    ):
   455	        return False
   456	    return True
   457	
   458	
   459	def _head_pin(value: object) -> tuple[int, str] | None:
   460	    if not isinstance(value, Mapping) or set(value) != {
   461	        "sequence",
   462	        "head_digest",
   463	        "ledger_schema",
   464	    }:
   465	        return None
   466	    sequence = value.get("sequence")
   467	    digest = value.get("head_digest")
   468	    if (
   469	        value.get("ledger_schema") != LEDGER_SCHEMA
   470	        or isinstance(sequence, bool)
   471	        or not isinstance(sequence, int)
   472	        or sequence < 0
   473	        or not _is_sha256(digest)
   474	        or (sequence == 0 and digest != GENESIS_DIGEST)
   475	    ):
   476	        return None
   477	    return sequence, str(digest)
   478	
   479	
   480	def _committed_pin_bytes(path: Path, repo_root: Path) -> bytes | None:
   481	    try:
   482	        relative = Path(path).resolve().relative_to(Path(repo_root).resolve()).as_posix()
   483	    except (OSError, ValueError):
   484	        return None
   485	    try:
   486	        completed = subprocess.run(
   487	            ["git", "show", f"HEAD:{relative}"],
   488	            cwd=repo_root,
   489	            check=True,
   490	            stdout=subprocess.PIPE,
   491	            stderr=subprocess.DEVNULL,
   492	        )
   493	    except (OSError, subprocess.CalledProcessError):
   494	        return None
   495	    return completed.stdout
   496	
   497	
   498	def _parse_ledger(raw: bytes) -> tuple[list[Mapping[str, Any]], set[str]]:
   499	    receipts: list[Mapping[str, Any]] = []
   500	    reasons: set[str] = set()
   501	    if not raw:
   502	        return receipts, reasons
   503	    try:
   504	        text = raw.decode("utf-8")
   505	    except UnicodeDecodeError:
   506	        return receipts, {"calibration_ledger_malformed"}
   507	    if not text.endswith("\n"):
   508	        reasons.add("calibration_ledger_malformed")
   509	    predecessor = GENESIS_DIGEST
   510	    expected_sequence = 1
   511	    seen_digests: set[str] = set()
   512	    for line in text.splitlines():
   513	        if not line.strip():
   514	            reasons.add("calibration_ledger_malformed")
   515	            continue
   516	        try:
   517	            value = json.loads(line)
   518	        except json.JSONDecodeError:
   519	            reasons.add("calibration_ledger_malformed")
   520	            continue
   521	        if not _valid_receipt_shape(value):
   522	            reasons.add("calibration_ledger_malformed")
   523	            continue
   524	        if (
   525	            value["sequence"] != expected_sequence
   526	            or value["predecessor_digest"] != predecessor
   527	            or value["receipt_digest"] in seen_digests
   528	        ):
   529	            reasons.add("calibration_ledger_chain_conflict")
   530	        expected_sequence += 1
   531	        predecessor = value["receipt_digest"]
   532	        seen_digests.add(predecessor)
   533	        receipts.append(value)
   534	    return receipts, reasons
   535	
   536	
   537	def _attempts_and_observations(
   538	    receipts: Sequence[Mapping[str, Any]],
   539	) -> tuple[list[LedgerObservation], set[str]]:
   540	    pending: dict[str, Mapping[str, Any]] = {}
   541	    finalized: dict[str, Mapping[str, Any]] = {}
   542	    reasons: set[str] = set()
   543	    for receipt in receipts:
   544	        attempt_id = str(receipt["attempt_id"])
   545	        if receipt["event"] in {
   546	            "reservation",
   547	            HISTORICAL_IMPORT_RESERVATION_EVENT,
   548	        }:
   549	            if attempt_id in pending or attempt_id in finalized:
   550	                reasons.add("calibration_ledger_attempt_conflict")
   551	            else:
   552	                pending[attempt_id] = receipt
   553	            continue
   554	        reservation = pending.get(attempt_id)
   555	        expected_final_event = (
   556	            HISTORICAL_IMPORT_FINALIZATION_EVENT
   557	            if reservation is not None
   558	            and reservation["event"] == HISTORICAL_IMPORT_RESERVATION_EVENT
   559	            else "finalization"
   560	        )
   561	        if (
   562	            reservation is None
   563	            or attempt_id in finalized
   564	            or receipt["event"] != expected_final_event
   565	        ):
   566	            reasons.add("calibration_ledger_attempt_conflict")
   567	        else:
   568	            finalized[attempt_id] = receipt
   569	    if set(pending) - set(finalized):
   570	        reasons.add("calibration_ledger_pending")
   571	
   572	    observations: list[LedgerObservation] = []
   573	    content_classification: dict[str, tuple[str, tuple[tuple[str, Any], ...]]] = {}
   574	    for attempt_id, receipt in sorted(
   575	        finalized.items(), key=lambda item: int(item[1]["sequence"])
   576	    ):
   577	        content_id = receipt.get("content_id")
   578	        epoch = dict(receipt["identity_epoch"])
   579	        if isinstance(content_id, str):
   580	            classification = (
   581	                (
   582	                    "unresolved"
   583	                    if receipt["disposition"] == "abandoned"
   584	                    else str(receipt["disposition"])
   585	                ),
   586	                tuple((field, epoch.get(field)) for field in IDENTITY_EPOCH_FIELDS),
   587	            )
   588	            previous = content_classification.get(content_id)
   589	            if previous is not None and previous != classification:
   590	                reasons.add("calibration_ledger_content_conflict")
   591	            content_classification[content_id] = classification
   592	        observations.append(
   593	            LedgerObservation(
   594	                sequence=int(receipt["sequence"]),
   595	                receipt_digest=str(receipt["receipt_digest"]),
   596	                attempt_id=attempt_id,
   597	                content_id=str(content_id) if isinstance(content_id, str) else None,
   598	                artifact_sha256=MappingProxyType(dict(receipt["artifact_sha256"])),
   599	                identity_epoch=MappingProxyType(epoch),
   600	                t1_bindings=MappingProxyType(dict(receipt["t1_bindings"])),
   601	                capture_wall_time_s=receipt.get("capture_wall_time_s"),
   602	                exact_bound_lexeme_s=receipt.get("exact_bound_lexeme_s"),
   603	                disposition=str(receipt["disposition"]),
   604	                custody_locator=str(receipt["custody_locator"]),
   605	                observation_kind=(
   606	                    "historical-import"
   607	                    if receipt["event"] == HISTORICAL_IMPORT_FINALIZATION_EVENT
   608	                    else "live-capture"
   609	                ),
   610	            )
   611	        )
   612	    return observations, reasons
   613	
   614	
   615	def _custody_reasons(
   616	    observations: Sequence[LedgerObservation], repo_root: Path
   617	) -> set[str]:
   618	    for observation in observations:
   619	        if not observation.artifact_sha256:
   620	            if observation.disposition == "abandoned":
   621	                continue
   622	            return {"calibration_ledger_custody_invalid"}
   623	        root = Path(observation.custody_locator)
   624	        if not root.is_absolute():
   625	            root = Path(repo_root) / root
   626	        for relative, expected in observation.artifact_sha256.items():
   627	            path = root / relative
   628	            try:
   629	                actual = hashlib.sha256(path.read_bytes()).hexdigest()
   630	            except OSError:
   631	                return {"calibration_ledger_custody_invalid"}
   632	            if actual != expected:
   633	                return {"calibration_ledger_custody_invalid"}
   634	    return set()
   635	
   636	
   637	def load_calibration_ledger_snapshot(
   638	    ledger_path: Path = DEFAULT_LEDGER_PATH,
   639	    head_pin_path: Path = DEFAULT_HEAD_PIN_PATH,
   640	    *,
   641	    baseline_sequence: int | None = None,
   642	    baseline_digest: str | None = None,
   643	    require_committed_pin: bool = True,
   644	    verify_custody: bool = True,
   645	    repo_root: Path = REPO_ROOT,
   646	) -> CalibrationLedgerSnapshot:
   647	    """Load, authenticate, and freeze exactly one ledger snapshot.
   648	
   649	    A proper physical prefix of the pin is classified explicitly as rollback;
   650	    any other physical/pinned disagreement is a stale-head mismatch.  The
   651	    baseline must occur at its exact sequence in the same complete chain.
   652	    This closes workflow omission, unregistered evidence, and rollback or
   653	    stale-head consumption; it does not defend against a malicious trusted
   654	    writer or a rewrite of both Git and the full ledger history.
   655	    """
   656	
   657	    ledger_path = Path(ledger_path)
   658	    head_pin_path = Path(head_pin_path)
   659	    reasons: set[str] = set()
   660	    try:
   661	        pin_raw = head_pin_path.read_bytes()
   662	        pin_value = json.loads(pin_raw)
   663	    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
   664	        pin_raw = b""
   665	        pin_value = None
   666	    pin = _head_pin(pin_value)
   667	    if pin is None:
   668	        reasons.add("calibration_ledger_malformed")
   669	        pinned_sequence, pinned_digest = 0, GENESIS_DIGEST
   670	    else:
   671	        pinned_sequence, pinned_digest = pin
   672	    try:
   673	        raw = ledger_path.read_bytes()
   674	    except OSError:
   675	        raw = b""
   676	        if pinned_sequence > 0:
   677	            reasons.add("calibration_ledger_missing")
   678	    genesis_development_bootstrap = (
   679	        pinned_sequence == 0
   680	        and pinned_digest == GENESIS_DIGEST
   681	        and not raw
   682	        and not ledger_path.exists()
   683	    )
   684	    if (
   685	        require_committed_pin
   686	        # The checked-in fixture starts at genesis.  Before its first commit,
   687	        # an absent physical ledger cannot license a claim (there are no
   688	        # endpoints); permitting this development-only empty view avoids a
   689	        # circular "commit before tests" bootstrap. Any physical byte or any
   690	        # non-genesis pin remains strictly commit-authenticated.
   691	        and not genesis_development_bootstrap
   692	        and _committed_pin_bytes(head_pin_path, repo_root) != pin_raw
   693	    ):
   694	        reasons.add("calibration_ledger_head_uncommitted")
   695	    receipts, parse_reasons = _parse_ledger(raw)
   696	    reasons.update(parse_reasons)
   697	    physical_sequence = len(receipts)
   698	    physical_digest = (
   699	        str(receipts[-1]["receipt_digest"]) if receipts else GENESIS_DIGEST
   700	    )
   701	    if (physical_sequence, physical_digest) != (pinned_sequence, pinned_digest):
   702	        if physical_sequence < pinned_sequence:
   703	            reasons.add("calibration_ledger_rollback")
   704	        else:
   705	            reasons.add("calibration_ledger_head_mismatch")
   706	    if baseline_sequence is not None or baseline_digest is not None:
   707	        if (
   708	            isinstance(baseline_sequence, bool)
   709	            or not isinstance(baseline_sequence, int)
   710	            or baseline_sequence < 0
   711	            or not _is_sha256(baseline_digest)
   712	        ):
   713	            reasons.add("calibration_ledger_baseline_missing")
   714	        else:
   715	            in_chain = (
   716	                baseline_digest == GENESIS_DIGEST
   717	                if baseline_sequence == 0
   718	                else baseline_sequence <= len(receipts)
   719	                and receipts[baseline_sequence - 1]["receipt_digest"]
   720	                == baseline_digest
   721	            )
   722	            if not in_chain or baseline_sequence > pinned_sequence:
   723	                reasons.add("calibration_ledger_baseline_missing")
   724	    observations, state_reasons = _attempts_and_observations(receipts)
   725	    reasons.update(state_reasons)
   726	    if verify_custody:
   727	        reasons.update(_custody_reasons(observations, repo_root))
   728	    return CalibrationLedgerSnapshot(
   729	        ledger_schema=LEDGER_SCHEMA,
   730	        ledger_path=ledger_path,
   731	        head_sequence=physical_sequence,
   732	        head_digest=physical_digest,
   733	        receipts=tuple(_frozen_mapping(receipt) for receipt in receipts),
   734	        observations=tuple(observations),
   735	        refusal_reasons=tuple(sorted(reasons)),
   736	        baseline_sequence=baseline_sequence,
   737	        baseline_digest=baseline_digest,
   738	    )
   739	
   740	
   400	        or rounding["operative_bracket_screen"].get("value_s")
   401	        != _D102_OPERATIVE_VALUES["bracket_screen_s"]
   402	        or not isinstance(rounding.get("preflight_level_screen"), Mapping)
   403	        or rounding["preflight_level_screen"].get("quantum_s")
   404	        != "0.000000000000001"
   405	        or rounding["preflight_level_screen"].get("value_s")
   406	        != _D102_OPERATIVE_VALUES["preflight_level_screen_s"]
   407	        or any(operatives.get(key) != item for key, item in _D102_OPERATIVE_VALUES.items())
   408	        or operatives.get("allowance_rule")
   409	        != "max(observed_drift_s,bracket_screen_s)"
   410	        or operatives.get("operative_bound_rule")
   411	        != "max(pre_b_fiducial_s,post_b_fiducial_s)+calibration_drift_allowance_s"
   412	        or operatives.get("embedding_count") != 1
   413	    ):
   414	        return False
   415	    screen = Decimal(_D102_OPERATIVE_VALUES["bracket_screen_s"])
   416	    maximum = Decimal(_D102_OPERATIVE_VALUES["maximum_budgetable_drift_s"])
   417	    excess = Decimal(_D102_OPERATIVE_VALUES["max_budgetable_excess_s"])
   418	    return (
   419	        (max(values) - min(values)).quantize(
   420	            Decimal("0.000001"), rounding=ROUND_HALF_EVEN
   421	        )
   422	        == screen
   423	        and max(values).quantize(
   424	            Decimal("0.000000000000001"), rounding=ROUND_HALF_EVEN
   425	        )
   426	        == Decimal(_D102_OPERATIVE_VALUES["preflight_level_screen_s"])
   427	        and screen + excess == maximum
   428	    )
   429	
   430	
   431	def load_calibration_acceptance_bound(
   432	    path: Path = DEFAULT_ACCEPTANCE_BOUND_PATH,
   433	) -> dict[str, Any] | None:
   434	    """Load the file-pinned D-102 acceptance artifact fail-closed."""
   435	
   436	    try:
   437	        raw = Path(path).read_bytes()
   438	    except OSError:
   439	        return None
   440	    return _acceptance_bound_from_authenticated_bytes(raw)
   441	
   442	
   443	def _acceptance_bound_from_authenticated_bytes(
   444	    raw: bytes,
   445	) -> dict[str, Any] | None:
   446	    """Parse acceptance bytes only when their role-indexed pin authenticates."""
   447	
   448	    try:
   449	        value = json.loads(raw)
   450	    except (UnicodeDecodeError, json.JSONDecodeError):
   451	        return None
   452	    # Any file route is authenticated by one of the two reviewed exact-byte
   453	    # states: the genesis fixture retained for pre-issuance tests, or the
   454	    # deterministically emitted issued artifact. A caller cannot turn an
   455	    # alternate self-consistent document into authority by choosing a path.
   456	    expected_sha256 = {
   457	        "schema_fixture_unissued": DEFAULT_ACCEPTANCE_BOUND_SHA256,
   458	        "issued": ISSUED_ACCEPTANCE_BOUND_SHA256,
   459	    }.get(value.get("artifact_role") if isinstance(value, Mapping) else None)
   460	    if hashlib.sha256(raw).hexdigest() != expected_sha256:
   461	        return None
   462	    if not _valid_acceptance_bound(value):
   463	        return None
   464	    return dict(value)
   465	
   466	
   467	def _authenticated_explicit_acceptance_bound(
   468	    value: Mapping[str, Any],
   469	) -> dict[str, Any] | None:
   470	    """Authenticate an in-memory artifact against the checked-in byte pin."""
   471	
   472	    pinned = load_calibration_acceptance_bound()
   473	    if pinned is None or dict(value) != pinned:
   474	        return None
   475	    return pinned
   476	
   477	
   478	def _acceptance_artifact_sha256(artifact: Mapping[str, Any]) -> str:
   479	    """Return the reviewed exact-byte pin for a validated artifact role."""
   480	
   481	    return (
   482	        ISSUED_ACCEPTANCE_BOUND_SHA256
   483	        if artifact.get("artifact_role") == "issued"
   484	        else DEFAULT_ACCEPTANCE_BOUND_SHA256
   485	    )
   486	
   487	
   488	def _valid_sha256(value: Any) -> bool:
   489	    return (
   490	        isinstance(value, str)
   491	        and len(value) == 64
   492	        and all(char in "0123456789abcdef" for char in value)
   493	    )
   494	
   495	
   496	def _binding_evidence_authentic(
   497	    evidence: Mapping[str, Any], bindings: Mapping[str, Any]
   498	) -> bool:
   499	    binding_evidence = evidence.get("binding_evidence")
   500	    binary = (
   501	        binding_evidence.get("powermetrics_binary")
   502	        if isinstance(binding_evidence, Mapping)
   503	        else None
   504	    )
   505	    power_policy = (
   506	        binding_evidence.get("power_policy")
   507	        if isinstance(binding_evidence, Mapping)
   508	        else None
   509	    )
   510	    # Canonical form MUST match the generation (powermetrics_fiducial) and
   511	    # reduce-side consumers byte-for-byte: ensure_ascii=False (delta-review
   512	    # P2 — the ASCII-default form made authentic non-ASCII binding vectors
   513	    # unmatchable as bracket candidates).
   514	    canonical = json.dumps(
   515	        dict(bindings),
   516	        sort_keys=True,
   517	        separators=(",", ":"),
   518	        ensure_ascii=False,
   519	        allow_nan=False,
   520	    ).encode("utf-8")

2026-08-07T20:22:46.819975Z ERROR codex_models_manager::manager: failed to renew cache TTL: missing field `base_instructions` at line 94 column 5
exec
/bin/zsh -lc "rg -n 'drift_widened_guarded_floor_j|point_floor_j|guarded_floor|floor.get|floor\\[' scripts/mint_floor_artifact.py | sed -n '1,240p'; rg -n 'AuthenticatedMember|metric_value_j|report_row|summary' scripts/mint_floor_artifact.py | sed -n '1,240p'; nl -ba scripts/mint_floor_artifact.py | sed -n '360,570p'; nl -ba scripts/mint_floor_artifact.py | sed -n '1240,1510p'" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u3
 succeeded in 0ms:
735:        floor.get("admissible_half_widths_j")
1381:            absolute.cell["floor"].get("drift_widened_guarded_floor_j"),
1386:            comparative.cell["floor"].get("drift_widened_guarded_floor_j"),
141:class AuthenticatedMember:
145:    metric_value_j: float
148:    summary: Mapping[str, Any]
168:    members: tuple[AuthenticatedMember, ...]
260:def _metric_value(summary: Mapping[str, Any]) -> float:
261:    phases = summary.get("phase_energy_j")
263:    return _finite(value, "summary phase_energy_j.decode")
386:    summary: Mapping[str, Any], bundle_id: str
388:    envelopes = summary.get("energy_anchor_shift_envelopes")
408:    bound_terms = summary.get("energy_bound_terms_j")
428:    operative_summary: Mapping[str, Any] | None = None,
429:) -> AuthenticatedMember:
456:    stored_summary, _ = _load_json_object(
457:        bundle_path / "summary_metrics.json", f"{bundle_id} summary"
459:    summary = (
460:        operative_summary
461:        if isinstance(operative_summary, Mapping)
462:        else stored_summary
464:    if summary.get("status") != "succeeded":
465:        raise MintError(f"{bundle_id}: source summary status is not succeeded")
475:    metric = _metric_value(summary)
477:        stored_row.get("metric_value_j"), f"{bundle_id} report metric"
481:    admissible_half_width = _source_admissible_half_width(summary, bundle_id)
497:    return AuthenticatedMember(
501:        metric_value_j=metric,
504:        summary=summary,
551:            bundle_id: summary
554:                (summary := session.summary_for(bundle_id)),
570:        summary, _ = _load_json_object(
571:            runs_root / bundle_id / "summary_metrics.json",
572:            f"{bundle_id} summary",
574:        summaries[bundle_id] = summary
815:    members: Sequence[AuthenticatedMember],
873:    members: Sequence[AuthenticatedMember],
884:        prechecks = member.summary.get("window_evidence_precheck")
935:        powers.append(member.metric_value_j / member_duration)
976:    member: AuthenticatedMember,
977:    report_row: Mapping[str, Any],
989:    ) != report_row.get("block_id"):
991:    position = report_row.get("position")
1106:            operative_summary=(
1114:    for member, report_row in zip(members, report_members, strict=True):
1117:            report_row,
1419:            "metric_value_j": member.metric_value_j,
1436:            position: member_by_id[ids[position]].metric_value_j
1457:                        "metric_value_j": values[position],
1517:        [member.metric_value_j for member in absolute.members],
1797:                    operative_summary=operative_summaries.get(
2013:            member.bundle_id: member.summary for member in component.members
   360	        "kernel_library": str(
   361	            prepare.get("kernel_library") or "unavailable"
   362	        ),
   363	        "model_artifact_sha256": artifact_sha256,
   364	        "quantization": dict(quantization),
   365	        "tokenizer_identity": tokenizer_identity,
   366	        "sampler_output_policy": {
   367	            "sampler": dict(sampler),
   368	            "output_policy": {
   369	                key: output_policy.get(key)
   370	                for key in ("name", "requested_tokens", "stop_condition")
   371	            },
   372	        },
   373	        "batching_concurrency_policy": str(
   374	            prepare.get("batching_concurrency_policy")
   375	            or "single-request sequential"
   376	        ),
   377	        "measurement_boundary_label": {
   378	            "boundary": device.get("boundary", "unavailable"),
   379	            "rails": device.get("rail_manifest"),
   380	        },
   381	        "telemetry_backend": telemetry_name,
   382	    }
   383	
   384	
   385	def _source_admissible_half_width(
   386	    summary: Mapping[str, Any], bundle_id: str
   387	) -> float:
   388	    envelopes = summary.get("energy_anchor_shift_envelopes")
   389	    envelope = (
   390	        envelopes.get("/phase_energy_j/decode")
   391	        if isinstance(envelopes, Mapping)
   392	        else None
   393	    )
   394	    if not isinstance(envelope, Mapping):
   395	        raise MintError(
   396	            f"{bundle_id}: decode anchor-shift envelope is unavailable"
   397	        )
   398	    point = _finite(envelope.get("point_j"), f"{bundle_id} anchor point")
   399	    lower = _finite(envelope.get("lower_j"), f"{bundle_id} anchor lower")
   400	    upper = _finite(envelope.get("upper_j"), f"{bundle_id} anchor upper")
   401	    max_delta = _finite(
   402	        envelope.get("max_abs_delta_j"),
   403	        f"{bundle_id} anchor max delta",
   404	        nonnegative=True,
   405	    )
   406	    if lower > point or upper < point:
   407	        raise MintError(f"{bundle_id}: anchor-shift envelope does not contain point")
   408	    bound_terms = summary.get("energy_bound_terms_j")
   409	    interpolation = (
   410	        bound_terms.get("E_interpolation_joint_edge_bound_j")
   411	        if isinstance(bound_terms, Mapping)
   412	        else None
   413	    )
   414	    interpolation_j = _finite(
   415	        interpolation,
   416	        f"{bundle_id} joint interpolation bound",
   417	        nonnegative=True,
   418	    )
   419	    return max(point - lower, upper - point, max_delta) + interpolation_j
   420	
   421	
   422	def _strict_bundle(
   423	    root: Path,
   424	    bundle_id: object,
   425	    stored_row: Mapping[str, Any],
   426	    strict_validator: StrictValidator,
   427	    *,
   428	    operative_summary: Mapping[str, Any] | None = None,
   429	) -> AuthenticatedMember:
   430	    if (
   431	        not isinstance(bundle_id, str)
   432	        or not bundle_id
   433	        or "\\" in bundle_id
   434	        or PurePosixPath(bundle_id).name != bundle_id
   435	        or bundle_id in {".", ".."}
   436	    ):
   437	        raise MintError("bundle_id must be a safe basename")
   438	    resolved_root = root.resolve()
   439	    bundle_path = (root / bundle_id).resolve()
   440	    try:
   441	        bundle_path.relative_to(resolved_root)
   442	    except ValueError as exc:
   443	        raise MintError(f"{bundle_id}: bundle path escapes its evidence root") from exc
   444	    try:
   445	        problems = tuple(strict_validator(bundle_path, True))
   446	    except Exception as exc:
   447	        raise MintError(
   448	            f"{bundle_id}: strict validation raised {type(exc).__name__}: {exc}"
   449	        ) from exc
   450	    if problems:
   451	        raise MintError(f"{bundle_id}: strict validation failed: {problems[0]}")
   452	    config, _ = _load_json_object(bundle_path / "config.json", f"{bundle_id} config")
   453	    metadata, _ = _load_json_object(
   454	        bundle_path / "metadata.json", f"{bundle_id} metadata"
   455	    )
   456	    stored_summary, _ = _load_json_object(
   457	        bundle_path / "summary_metrics.json", f"{bundle_id} summary"
   458	    )
   459	    summary = (
   460	        operative_summary
   461	        if isinstance(operative_summary, Mapping)
   462	        else stored_summary
   463	    )
   464	    if summary.get("status") != "succeeded":
   465	        raise MintError(f"{bundle_id}: source summary status is not succeeded")
   466	    try:
   467	        bundle_sha256 = complete_bundle_sha256(bundle_path)
   468	    except ValueError as exc:
   469	        raise MintError(f"{bundle_id}: cannot hash complete bundle: {exc}") from exc
   470	    config_sha256 = _sha256_file(bundle_path / "config.json", f"{bundle_id} config")
   471	    if bundle_sha256 != stored_row.get("bundle_sha256"):
   472	        raise MintError(f"{bundle_id}: report bundle_sha256 does not match source bytes")
   473	    if config_sha256 != stored_row.get("config_sha256"):
   474	        raise MintError(f"{bundle_id}: report config_sha256 does not match source bytes")
   475	    metric = _metric_value(summary)
   476	    stored_metric = _finite(
   477	        stored_row.get("metric_value_j"), f"{bundle_id} report metric"
   478	    )
   479	    if not math.isclose(metric, stored_metric, rel_tol=1e-12, abs_tol=1e-12):
   480	        raise MintError(f"{bundle_id}: report metric does not match source bytes")
   481	    admissible_half_width = _source_admissible_half_width(summary, bundle_id)
   482	    if "anchor_shift_bound_j" in stored_row:
   483	        stored_width = _finite(
   484	            stored_row.get("anchor_shift_bound_j"),
   485	            f"{bundle_id} report anchor width",
   486	            nonnegative=True,
   487	        )
   488	        if not math.isclose(
   489	            admissible_half_width,
   490	            stored_width,
   491	            rel_tol=1e-12,
   492	            abs_tol=1e-12,
   493	        ):
   494	            raise MintError(
   495	                f"{bundle_id}: report anchor width does not match source bytes"
   496	            )
   497	    return AuthenticatedMember(
   498	        bundle_id=bundle_id,
   499	        bundle_sha256=bundle_sha256,
   500	        config_sha256=config_sha256,
   501	        metric_value_j=metric,
   502	        raw_config=config,
   503	        metadata=metadata,
   504	        summary=summary,
   505	        admissible_half_width_j=admissible_half_width,
   506	    )
   507	
   508	
   509	def _authenticated_consumption_summaries(
   510	    runs_root: Path,
   511	    referenced_bundle_ids: set[str],
   512	    evaluation_basis_sha256: str,
   513	    *,
   514	    target_bundle_ids: set[str],
   515	    consumption_semantics_id: str | None = None,
   516	    calibration_ledger_snapshot: CalibrationLedgerSnapshot | None = None,
   517	) -> tuple[Mapping[str, Mapping[str, Any]], str]:
   518	    """Replay the authenticated whole-window consumption semantics once."""
   519	
   520	    session = AuthenticatedConsumptionSession(
   521	        runs_root,
   522	        referenced_bundle_ids,
   523	        evaluation_basis_sha256=evaluation_basis_sha256,
   524	        consumption_semantics_id=(
   525	            consumption_semantics_id or MAX_BRACKET_CONSUMPTION_SEMANTICS_ID
   526	        ),
   527	        calibration_ledger_snapshot=calibration_ledger_snapshot,
   528	    )
   529	    reasons = whole_window_refusal_reasons(
   530	        runs_root,
   531	        referenced_bundle_ids,
   532	        evaluation_basis_sha256=evaluation_basis_sha256,
   533	        consumption_session=session,
   534	        consumption_semantics_id=consumption_semantics_id,
   535	    )
   536	    if reasons:
   537	        raise MintError(
   538	            "authenticated whole-window consumption refused: " + reasons[0]
   539	        )
   540	    if session.ready:
   541	        for bundle_id in sorted(target_bundle_ids):
   542	            target_reasons = session.path_refusal_reasons.get(
   543	                bundle_id, {}
   544	            ).get(TARGET_PRECHECK_PATH, ())
   545	            if target_reasons:
   546	                raise MintError(
   547	                    f"{bundle_id}: authenticated target metric refused: "
   548	                    f"{target_reasons[0]}"
   549	                )
   550	        summaries = {
   551	            bundle_id: summary
   552	            for bundle_id in referenced_bundle_ids
   553	            if isinstance(
   554	                (summary := session.summary_for(bundle_id)),
   555	                Mapping,
   556	            )
   557	        }
   558	        if set(summaries) != referenced_bundle_ids:
   559	            raise MintError(
   560	                "authenticated whole-window consumption omitted source members"
   561	            )
   562	        return summaries, getattr(
   563	            session,
   564	            "consumption_semantics_id",
   565	            consumption_semantics_id or MAX_BRACKET_CONSUMPTION_SEMANTICS_ID,
   566	        )
   567	
   568	    summaries: dict[str, Mapping[str, Any]] = {}
   569	    for bundle_id in referenced_bundle_ids:
   570	        summary, _ = _load_json_object(
  1240	    if not isinstance(bindings, Mapping):
  1241	        raise MintError("target spec cell lacks condition-family definitions")
  1242	    key = "all" if component.kind == "absolute" else "A"
  1243	    binding = bindings.get(key)
  1244	    if not isinstance(binding, Mapping):
  1245	        raise MintError(f"target spec cell lacks condition-family binding {key!r}")
  1246	    return binding
  1247	
  1248	
  1249	def _diagnostics_are_nonpublishing(
  1250	    value: object, *, diagnostic_context: bool = False
  1251	) -> bool:
  1252	    if isinstance(value, Mapping):
  1253	        is_diagnostic = diagnostic_context or (
  1254	            value.get("label") == "repeatability_diagnostic"
  1255	        )
  1256	        if is_diagnostic and value.get("published_claim_floor") is not False:
  1257	            return False
  1258	        for key, child in value.items():
  1259	            if key == "published_claim_floor" and child is not False:
  1260	                return False
  1261	            if not _diagnostics_are_nonpublishing(
  1262	                child,
  1263	                diagnostic_context=key in {
  1264	                    "point_floor_diagnostic",
  1265	                    "point_floor_diagnostics",
  1266	                },
  1267	            ):
  1268	                return False
  1269	    elif isinstance(value, list):
  1270	        return all(_diagnostics_are_nonpublishing(child) for child in value)
  1271	    return True
  1272	
  1273	
  1274	def pre_registration_gate(
  1275	    *,
  1276	    plan: Mapping[str, Any],
  1277	    plan_sha256: str,
  1278	    absolute: AuthenticatedComponent,
  1279	    comparative: AuthenticatedComponent,
  1280	) -> None:
  1281	    """Enforce the ratified mint-1 literals before any builder call."""
  1282	
  1283	    if plan_sha256 != PLAN_SHA256:
  1284	        raise MintError("pre-registration gate: calibration plan sha256 mismatch")
  1285	    if (
  1286	        plan.get("plan_id") != "p2-015-window-a-m3max-qwen25-1p5b-v1"
  1287	        or plan.get("calibration_scope") != PLAN_DECLARED_SCOPE
  1288	    ):
  1289	        raise MintError("pre-registration gate: calibration plan identity mismatch")
  1290	    if absolute.evidence_root_id != "a10" or comparative.evidence_root_id != "window_c":
  1291	        raise MintError(
  1292	            "pre-registration gate: components require distinct a10/window_c roots"
  1293	        )
  1294	    if (
  1295	        absolute.whole_window_evaluation_basis_sha256
  1296	        != A10_EVALUATION_BASIS_SHA256
  1297	        or comparative.whole_window_evaluation_basis_sha256
  1298	        != WINDOW_C_EVALUATION_BASIS_SHA256
  1299	    ):
  1300	        raise MintError("pre-registration gate: component evaluation bases mismatch")
  1301	    if (
  1302	        absolute.evaluation_basis_member_count != A10_EVALUATION_BASIS_MEMBERS
  1303	        or comparative.evaluation_basis_member_count
  1304	        != WINDOW_C_EVALUATION_BASIS_MEMBERS
  1305	    ):
  1306	        raise MintError("pre-registration gate: evaluation-basis member count mismatch")
  1307	    if (
  1308	        len(_spec_member_ids(absolute.spec)) != A10_SPEC_MEMBERS
  1309	        or len(_spec_member_ids(comparative.spec)) != WINDOW_C_SPEC_MEMBERS
  1310	    ):
  1311	        raise MintError("pre-registration gate: extraction-spec membership mismatch")
  1312	    if (
  1313	        absolute.cell["floor"].get("n") != EXPECTED_ABSOLUTE_N
  1314	        or len(absolute.members) != EXPECTED_ABSOLUTE_N
  1315	        or comparative.cell["floor"].get("n") != EXPECTED_COMPARATIVE_N_BLOCKS
  1316	        or len(comparative.members) != 4 * EXPECTED_COMPARATIVE_N_BLOCKS
  1317	    ):
  1318	        raise MintError("pre-registration gate: absolute/comparative n mismatch")
  1319	    if absolute.order_manifest.get("manifest_id") != A10_ORDER_MANIFEST_ID:
  1320	        raise MintError("pre-registration gate: a10 order manifest mismatch")
  1321	    if (
  1322	        comparative.order_manifest.get("manifest_id")
  1323	        != WINDOW_C_ORDER_MANIFEST_ID
  1324	    ):
  1325	        raise MintError("pre-registration gate: window-C order manifest mismatch")
  1326	    if (
  1327	        absolute.order_manifest.get("calibration_plan_sha256") != PLAN_SHA256
  1328	        or comparative.order_manifest.get("calibration_plan_sha256")
  1329	        != PLAN_SHA256
  1330	        or absolute.order_manifest.get("plan_id") != plan.get("plan_id")
  1331	        or comparative.order_manifest.get("plan_id") != plan.get("plan_id")
  1332	    ):
  1333	        raise MintError("pre-registration gate: order manifest plan pin mismatch")
  1334	    if absolute.consumption_semantics_id not in _SEMANTICS_IDS or (
  1335	        comparative.consumption_semantics_id not in _SEMANTICS_IDS
  1336	    ):
  1337	        raise MintError("pre-registration gate: unknown consumption semantics")
  1338	
  1339	    absolute_binding = _definition_binding(absolute)
  1340	    comparative_bindings = comparative.spec_cell.get(
  1341	        "condition_family_definitions"
  1342	    )
  1343	    if (
  1344	        not isinstance(comparative_bindings, Mapping)
  1345	        or comparative_bindings.get("A") != comparative_bindings.get("B")
  1346	        or absolute_binding != comparative_bindings.get("A")
  1347	        or absolute_binding.get("condition_family_id") != CONDITION_FAMILY_ID
  1348	        or absolute_binding.get("condition_family_sha256")
  1349	        != CONDITION_FAMILY_SHA256
  1350	        or absolute_binding.get("condition_family_definition", {}).get(
  1351	            "abba_alias_relation"
  1352	        )
  1353	        != "A_equals_B"
  1354	    ):
  1355	        raise MintError("pre-registration gate: window-C is not the pinned A==B null")
  1356	    allowance = _finite(
  1357	        absolute.whole_window_drift_allowance.get("allowance_j"),
  1358	        "a10 whole-window allowance",
  1359	        nonnegative=True,
  1360	    )
  1361	    if not math.isclose(
  1362	        allowance, A10_DRIFT_ALLOWANCE_J, rel_tol=0.0, abs_tol=1e-12
  1363	    ):
  1364	        raise MintError("pre-registration gate: a10 drift allowance mismatch")
  1365	    comparative_allowance = _finite(
  1366	        comparative.whole_window_drift_allowance.get("allowance_j"),
  1367	        "window-C comparative whole-window allowance",
  1368	        nonnegative=True,
  1369	    )
  1370	    if not math.isclose(
  1371	        comparative_allowance,
  1372	        WINDOW_C_DRIFT_ALLOWANCE_J,
  1373	        rel_tol=0.0,
  1374	        abs_tol=1e-12,
  1375	    ):
  1376	        raise MintError(
  1377	            "pre-registration gate: window-C drift allowance mismatch"
  1378	        )
  1379	    operative = max(
  1380	        _finite(
  1381	            absolute.cell["floor"].get("drift_widened_guarded_floor_j"),
  1382	            "absolute operative floor",
  1383	            nonnegative=True,
  1384	        ),
  1385	        _finite(
  1386	            comparative.cell["floor"].get("drift_widened_guarded_floor_j"),
  1387	            "comparative operative floor",
  1388	            nonnegative=True,
  1389	        ),
  1390	    )
  1391	    if format(operative, ".6f") != EXPECTED_OPERATIVE_FLOOR_TEXT:
  1392	        raise MintError("pre-registration gate: formatted operative floor mismatch")
  1393	    if not _diagnostics_are_nonpublishing(absolute.report) or not (
  1394	        _diagnostics_are_nonpublishing(comparative.report)
  1395	    ):
  1396	        raise MintError(
  1397	            "pre-registration gate: diagnostic floor is marked as published"
  1398	        )
  1399	    if absolute.scientific_config_identity_sha256 != (
  1400	        comparative.scientific_config_identity_sha256
  1401	    ):
  1402	        raise MintError("pre-registration gate: scientific config identity mismatch")
  1403	    if absolute.source_regime["stack_identity_sha256"] != (
  1404	        comparative.source_regime["stack_identity_sha256"]
  1405	    ):
  1406	        raise MintError("pre-registration gate: stack identity mismatch")
  1407	    if absolute.backend != comparative.backend:
  1408	        raise MintError("pre-registration gate: telemetry backend mismatch")
  1409	
  1410	
  1411	def _absolute_observations(
  1412	    component: AuthenticatedComponent,
  1413	) -> list[Mapping[str, Any]]:
  1414	    return [
  1415	        {
  1416	            "bundle_id": member.bundle_id,
  1417	            "bundle_sha256": member.bundle_sha256,
  1418	            "config_sha256": member.config_sha256,
  1419	            "metric_value_j": member.metric_value_j,
  1420	        }
  1421	        for member in component.members
  1422	    ]
  1423	
  1424	
  1425	def _comparative_blocks(
  1426	    component: AuthenticatedComponent,
  1427	) -> tuple[list[Mapping[str, Any]], list[float]]:
  1428	    blocks = component.spec_cell["blocks"]
  1429	    member_by_id = {member.bundle_id: member for member in component.members}
  1430	    result: list[Mapping[str, Any]] = []
  1431	    deltas: list[float] = []
  1432	    for spec_block in blocks:
  1433	        block_id = spec_block["block_id"]
  1434	        ids = spec_block["members"]
  1435	        values = {
  1436	            position: member_by_id[ids[position]].metric_value_j
  1437	            for position in _ABBA_POSITIONS
  1438	        }
  1439	        delta = abba_delta(
  1440	            values["A1"], values["B1"], values["B2"], values["A2"]
  1441	        )
  1442	        deltas.append(delta)
  1443	        result.append(
  1444	            {
  1445	                "block_id": block_id,
  1446	                "executed_labels": ["A", "B", "B", "A"],
  1447	                "members": [
  1448	                    {
  1449	                        "position": position,
  1450	                        "bundle_id": member_by_id[ids[position]].bundle_id,
  1451	                        "bundle_sha256": member_by_id[
  1452	                            ids[position]
  1453	                        ].bundle_sha256,
  1454	                        "config_sha256": member_by_id[
  1455	                            ids[position]
  1456	                        ].config_sha256,
  1457	                        "metric_value_j": values[position],
  1458	                    }
  1459	                    for position in _ABBA_POSITIONS
  1460	                ],
  1461	                "delta_j": delta,
  1462	            }
  1463	        )
  1464	    return result, deltas
  1465	
  1466	
  1467	def _component_provenance(
  1468	    component: AuthenticatedComponent,
  1469	) -> Mapping[str, Any]:
  1470	    return {
  1471	        "calibration_cell_id": component.calibration_cell_id,
  1472	        "evidence_root_id": component.evidence_root_id,
  1473	        "order_manifest": {
  1474	            "manifest_id": component.order_manifest["manifest_id"],
  1475	            "sha256": component.order_manifest_sha256,
  1476	        },
  1477	        "campaign_log": {"sha256": component.campaign_log_sha256},
  1478	        "extraction_report": {"sha256": component.report_sha256},
  1479	        "extraction_spec": {"sha256": component.spec_sha256},
  1480	        "bundle_ids": [member.bundle_id for member in component.members],
  1481	        "bundle_sha256s": [
  1482	            member.bundle_sha256 for member in component.members
  1483	        ],
  1484	        "source_regime": component.source_regime,
  1485	    }
  1486	
  1487	
  1488	def mint_authenticated_artifact(
  1489	    *,
  1490	    artifact_id: str,
  1491	    plan: Mapping[str, Any],
  1492	    plan_sha256: str,
  1493	    calibration_plan_relative_path: str,
  1494	    absolute: AuthenticatedComponent,
  1495	    comparative: AuthenticatedComponent,
  1496	    project_commit: str,
  1497	    project_tree_state: str,
  1498	) -> dict[str, Any]:
  1499	    """Run the gate, then construct and validate the one governed artifact."""
  1500	
  1501	    pre_registration_gate(
  1502	        plan=plan,
  1503	        plan_sha256=plan_sha256,
  1504	        absolute=absolute,
  1505	        comparative=comparative,
  1506	    )
  1507	    relative_plan = _safe_relative_posix(
  1508	        calibration_plan_relative_path,
  1509	        "calibration_plan.relative_path",
  1510	    )

2026-08-07T20:22:57.219011Z ERROR codex_models_manager::manager: failed to renew cache TTL: missing field `base_instructions` at line 94 column 5
exec
/bin/zsh -lc "nl -ba scripts/mint_floor_artifact.py | sed -n '1510,1665p'; rg -n 'build_floor|floor_abs_j|drift_widened_guarded_floor_j|mean_j|stddev' scripts/mint_floor_artifact.py | tail -120; rg -n 'def build_absolute_record|def build_comparative_record|def build_floor_cell' joulewise/detection_floor.py" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u3
 succeeded in 0ms:
  1510	    )
  1511	    if re.fullmatch(r"[0-9a-f]{40}", project_commit) is None:
  1512	        raise MintError("project_commit must be 40 lowercase hex chars")
  1513	    if project_tree_state not in {"clean", "dirty"}:
  1514	        raise MintError("project_tree_state must be 'clean' or 'dirty'")
  1515	
  1516	    abs_estimate = absolute_false_effect_floor(
  1517	        [member.metric_value_j for member in absolute.members],
  1518	        admissible_half_widths_j=absolute.widths_j,
  1519	    )
  1520	    absolute_record = build_absolute_record(
  1521	        abs_estimate,
  1522	        _absolute_observations(absolute),
  1523	        consumption_semantics_id=absolute.consumption_semantics_id,
  1524	        whole_window_drift_allowance=absolute.whole_window_drift_allowance,
  1525	    )
  1526	    comparative_blocks, deltas = _comparative_blocks(comparative)
  1527	    cmp_estimate = comparative_false_effect_floor(
  1528	        deltas,
  1529	        admissible_half_widths_j=comparative.widths_j,
  1530	    )
  1531	    comparative_record = build_comparative_record(
  1532	        cmp_estimate,
  1533	        comparative_blocks,
  1534	        consumption_semantics_id=comparative.consumption_semantics_id,
  1535	        whole_window_drift_allowance=comparative.whole_window_drift_allowance,
  1536	    )
  1537	
  1538	    binding = _definition_binding(absolute)
  1539	    definition = binding["condition_family_definition"]
  1540	    if canonical_domain_sha256(CONDITION_FAMILY_DOMAIN, definition) != (
  1541	        CONDITION_FAMILY_SHA256
  1542	    ):
  1543	        raise MintError("condition-family definition hash changed after gate")
  1544	    cell = build_floor_cell(
  1545	        cell_id=CELL_ID,
  1546	        key={
  1547	            "backend": absolute.backend,
  1548	            "metric": METRIC,
  1549	            "window_class": WINDOW_CLASS,
  1550	            "condition_family_id": CONDITION_FAMILY_ID,
  1551	            "condition_family_definition": definition,
  1552	            "condition_family_sha256": CONDITION_FAMILY_SHA256,
  1553	        },
  1554	        eligibility={
  1555	            "use_role": "primary_claim_gate",
  1556	            "minimum_claim_n": 10,
  1557	            "status": "claim_ready",
  1558	            "claim_usable": True,
  1559	            "reason_codes": [],
  1560	        },
  1561	        absolute=absolute_record,
  1562	        comparative=comparative_record,
  1563	        transport_group_id=TRANSPORT_GROUP_ID,
  1564	        provenance={
  1565	            "absolute": _component_provenance(absolute),
  1566	            "comparative": _component_provenance(comparative),
  1567	        },
  1568	    )
  1569	    group = build_transport_group(
  1570	        transport_group_id=TRANSPORT_GROUP_ID,
  1571	        backend=absolute.backend,
  1572	        metric=METRIC,
  1573	        window_class=WINDOW_CLASS,
  1574	        stack_identity=cell["source_regime"]["stack_identity"],
  1575	        source_cells=[cell],
  1576	        allowed_consumer_condition_families=[
  1577	            {
  1578	                "condition_family_id": CONDITION_FAMILY_ID,
  1579	                "condition_family_definition": definition,
  1580	                "condition_family_sha256": CONDITION_FAMILY_SHA256,
  1581	            }
  1582	        ],
  1583	    )
  1584	    artifact = build_floor_artifact(
  1585	        artifact_id=artifact_id,
  1586	        calibration_scope=CALIBRATION_SCOPE,
  1587	        source_class=SOURCE_CLASS,
  1588	        provenance={
  1589	            "calibration_plan": {
  1590	                "plan_id": plan["plan_id"],
  1591	                "declared_calibration_scope": PLAN_DECLARED_SCOPE,
  1592	                "relative_path": relative_plan,
  1593	                "sha256": plan_sha256,
  1594	            },
  1595	            "mint_tool_version": MINT_TOOL_VERSION,
  1596	            "implementation": {
  1597	                "project_commit": project_commit,
  1598	                "project_tree_state": project_tree_state,
  1599	                "python_package": "joulewise",
  1600	            },
  1601	        },
  1602	        cells=[cell],
  1603	        transport_groups=[group],
  1604	    )
  1605	    artifact_cell = artifact["cells"][0]
  1606	    if format(artifact_cell["floor_gate_j"], ".6f") != (
  1607	        EXPECTED_OPERATIVE_FLOOR_TEXT
  1608	    ):
  1609	        raise MintError("post-construction floor_gate_j headline mismatch")
  1610	    if artifact_cell["floor_gate_j"] != group["composed_floor_gate_j"]:
  1611	        raise MintError("post-construction transport headline mismatch")
  1612	    errors = validate_floor_artifact(artifact)
  1613	    if errors:
  1614	        raise MintError(f"constructed artifact is invalid: {errors[0]}")
  1615	    _assert_path_independent(artifact)
  1616	    return artifact
  1617	
  1618	
  1619	def _resolve_plan_path(floor_path: Path, relative_path: object) -> Path:
  1620	    relative = _safe_relative_posix(
  1621	        relative_path, "artifact.provenance.calibration_plan.relative_path"
  1622	    )
  1623	    root = floor_path.parent.resolve()
  1624	    candidate = (root / relative).resolve()
  1625	    try:
  1626	        candidate.relative_to(root)
  1627	    except ValueError as exc:
  1628	        raise MintError("calibration plan escapes the artifact root") from exc
  1629	    return candidate
  1630	
  1631	
  1632	def _record_rows(component_name: str, cell: Mapping[str, Any]) -> list[Mapping]:
  1633	    record = cell.get(component_name)
  1634	    if not isinstance(record, Mapping):
  1635	        return []
  1636	    if component_name == "absolute":
  1637	        rows = record.get("bundle_observations")
  1638	        return list(rows) if isinstance(rows, list) else []
  1639	    result: list[Mapping] = []
  1640	    blocks = record.get("blocks")
  1641	    if isinstance(blocks, list):
  1642	        for block in blocks:
  1643	            members = block.get("members") if isinstance(block, Mapping) else None
  1644	            if isinstance(members, list):
  1645	                result.extend(row for row in members if isinstance(row, Mapping))
  1646	    return result
  1647	
  1648	
  1649	def _binding_cache_key(
  1650	    root: Path,
  1651	    basis_sha256: str,
  1652	    rows: Sequence[Mapping[str, Any]],
  1653	) -> tuple[str, str, tuple[tuple[str, str], ...]]:
  1654	    members: list[tuple[str, str]] = []
  1655	    for row in rows:
  1656	        bundle_id = row.get("bundle_id")
  1657	        bundle_sha256 = row.get("bundle_sha256")
  1658	        if not isinstance(bundle_id, str) or not isinstance(bundle_sha256, str):
  1659	            raise MintError("component rows lack bundle identity hashes")
  1660	        members.append((bundle_id, bundle_sha256))
  1661	    return (str(root.resolve()), basis_sha256, tuple(members))
  1662	
  1663	
  1664	def bind_floor_artifact_evidence(
  1665	    artifact: Mapping[str, Any],
36:    build_floor_artifact,
37:    build_floor_cell,
1381:            absolute.cell["floor"].get("drift_widened_guarded_floor_j"),
1386:            comparative.cell["floor"].get("drift_widened_guarded_floor_j"),
1544:    cell = build_floor_cell(
1584:    artifact = build_floor_artifact(
862:def build_absolute_record(
902:def build_comparative_record(
1004:def build_floor_cell(

2026-08-07T20:23:01.901459Z ERROR codex_models_manager::manager: failed to renew cache TTL: missing field `base_instructions` at line 94 column 5
exec
/bin/zsh -lc "nl -ba scripts/mint_floor_artifact_generalized.py | sed -n '2220,2580p'; nl -ba tests/test_mint_floor_artifact_generalized.py | sed -n '1620,1805p'; nl -ba tests/test_mint_floor_artifact_generalized.py | sed -n '1880,1980p'" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u3
 succeeded in 0ms:
  2220	        normalized.append(dict(row))
  2221	    if observed != expected:
  2222	        raise MintError(f"{label} does not match the transport allowlist pins")
  2223	    return normalized
  2224	
  2225	
  2226	def _v2_pre_registration_gate(
  2227	    *,
  2228	    core: ModuleType,
  2229	    producer: Mapping[str, Any],
  2230	    cell_pins: Mapping[str, Any],
  2231	    plan: Mapping[str, Any],
  2232	    absolute: Any,
  2233	    comparative: Any,
  2234	) -> Mapping[str, Any]:
  2235	    plan_pins = producer["plan"]
  2236	    if absolute.order_manifest.get("calibration_plan_sha256") != plan_pins[
  2237	        "sha256"
  2238	    ] or comparative.order_manifest.get("calibration_plan_sha256") != plan_pins[
  2239	        "sha256"
  2240	    ]:
  2241	        raise MintError("v2 pre-registration gate: order-manifest plan sha mismatch")
  2242	    if absolute.order_manifest.get("plan_id") != plan.get(
  2243	        "plan_id"
  2244	    ) or comparative.order_manifest.get("plan_id") != plan.get("plan_id"):
  2245	        raise MintError("v2 pre-registration gate: order-manifest plan id mismatch")
  2246	    absolute_binding = core._definition_binding(absolute)
  2247	    comparative_bindings = comparative.spec_cell.get(
  2248	        "condition_family_definitions"
  2249	    )
  2250	    if (
  2251	        not isinstance(comparative_bindings, Mapping)
  2252	        or comparative_bindings.get("A") != comparative_bindings.get("B")
  2253	        or absolute_binding != comparative_bindings.get("A")
  2254	        or absolute_binding.get("condition_family_id")
  2255	        != cell_pins["condition_family_id"]
  2256	        or absolute_binding.get("condition_family_sha256")
  2257	        != cell_pins["condition_family_sha256"]
  2258	        or absolute_binding.get("condition_family_definition", {}).get(
  2259	            "abba_alias_relation"
  2260	        )
  2261	        != "A_equals_B"
  2262	    ):
  2263	        raise MintError(
  2264	            "v2 pre-registration gate: components are not the pinned A==B null"
  2265	        )
  2266	    if not core._diagnostics_are_nonpublishing(
  2267	        absolute.report
  2268	    ) or not core._diagnostics_are_nonpublishing(comparative.report):
  2269	        raise MintError(
  2270	            "v2 pre-registration gate: diagnostic floor is marked as published"
  2271	        )
  2272	    if absolute.scientific_config_identity_sha256 != (
  2273	        comparative.scientific_config_identity_sha256
  2274	    ):
  2275	        raise MintError(
  2276	            "v2 pre-registration gate: scientific config identity mismatch"
  2277	        )
  2278	    if absolute.source_regime["stack_identity_sha256"] != (
  2279	        comparative.source_regime["stack_identity_sha256"]
  2280	    ):
  2281	        raise MintError("v2 pre-registration gate: stack identity mismatch")
  2282	    if absolute.backend != comparative.backend:
  2283	        raise MintError("v2 pre-registration gate: telemetry backend mismatch")
  2284	    return absolute_binding
  2285	
  2286	
  2287	def _mint_v2_cell_artifact(
  2288	    *,
  2289	    core: ModuleType,
  2290	    producer: Mapping[str, Any],
  2291	    cell_pins: Mapping[str, Any],
  2292	    plan: Mapping[str, Any],
  2293	    project_commit: str,
  2294	    project_tree_state: str,
  2295	    absolute: Any,
  2296	    comparative: Any,
  2297	) -> Mapping[str, Any]:
  2298	    """Construct one v2 cell without invoking either v1 literal derivation."""
  2299	
  2300	    plan_pins = producer["plan"]
  2301	    binding = _v2_pre_registration_gate(
  2302	        core=core,
  2303	        producer=producer,
  2304	        cell_pins=cell_pins,
  2305	        plan=plan,
  2306	        absolute=absolute,
  2307	        comparative=comparative,
  2308	    )
  2309	    relative_plan = core._safe_relative_posix(
  2310	        plan_pins["relative_path"], "calibration_plan.relative_path"
  2311	    )
  2312	    absolute_estimate = core.absolute_false_effect_floor(
  2313	        [member.metric_value_j for member in absolute.members],
  2314	        admissible_half_widths_j=absolute.widths_j,
  2315	    )
  2316	    absolute_record = core.build_absolute_record(
  2317	        absolute_estimate,
  2318	        core._absolute_observations(absolute),
  2319	        consumption_semantics_id=absolute.consumption_semantics_id,
  2320	        whole_window_drift_allowance=absolute.whole_window_drift_allowance,
  2321	    )
  2322	    comparative_blocks, deltas = core._comparative_blocks(comparative)
  2323	    comparative_estimate = core.comparative_false_effect_floor(
  2324	        deltas,
  2325	        admissible_half_widths_j=comparative.widths_j,
  2326	    )
  2327	    comparative_record = core.build_comparative_record(
  2328	        comparative_estimate,
  2329	        comparative_blocks,
  2330	        consumption_semantics_id=comparative.consumption_semantics_id,
  2331	        whole_window_drift_allowance=comparative.whole_window_drift_allowance,
  2332	    )
  2333	    definition = binding["condition_family_definition"]
  2334	    if core.canonical_domain_sha256(
  2335	        core.CONDITION_FAMILY_DOMAIN, definition
  2336	    ) != cell_pins["condition_family_sha256"]:
  2337	        raise MintError("condition-family definition hash changed after v2 gate")
  2338	    cell = core.build_floor_cell(
  2339	        cell_id=cell_pins["cell_id"],
  2340	        key={
  2341	            "backend": absolute.backend,
  2342	            "metric": cell_pins["metric"],
  2343	            "window_class": cell_pins["window_class"],
  2344	            "condition_family_id": cell_pins["condition_family_id"],
  2345	            "condition_family_definition": definition,
  2346	            "condition_family_sha256": cell_pins["condition_family_sha256"],
  2347	        },
  2348	        eligibility={
  2349	            "use_role": "primary_claim_gate",
  2350	            "minimum_claim_n": cell_pins["absolute"]["expected_n"],
  2351	            "status": "claim_ready",
  2352	            "claim_usable": True,
  2353	            "reason_codes": [],
  2354	        },
  2355	        absolute=absolute_record,
  2356	        comparative=comparative_record,
  2357	        transport_group_id=cell_pins["transport_group_id"],
  2358	        provenance={
  2359	            "absolute": core._component_provenance(absolute),
  2360	            "comparative": core._component_provenance(comparative),
  2361	        },
  2362	    )
  2363	    group = core.build_transport_group(
  2364	        transport_group_id=cell_pins["transport_group_id"],
  2365	        backend=absolute.backend,
  2366	        metric=cell_pins["metric"],
  2367	        window_class=cell_pins["window_class"],
  2368	        stack_identity=cell["source_regime"]["stack_identity"],
  2369	        source_cells=[cell],
  2370	        allowed_consumer_condition_families=[
  2371	            {
  2372	                "condition_family_id": cell_pins["condition_family_id"],
  2373	                "condition_family_definition": definition,
  2374	                "condition_family_sha256": cell_pins[
  2375	                    "condition_family_sha256"
  2376	                ],
  2377	            }
  2378	        ],
  2379	    )
  2380	    artifact = core.build_floor_artifact(
  2381	        artifact_id=producer["component_artifact"]["artifact_id"],
  2382	        calibration_scope=plan_pins["artifact_calibration_scope"],
  2383	        source_class="prospective",
  2384	        provenance={
  2385	            "calibration_plan": {
  2386	                "plan_id": plan["plan_id"],
  2387	                "declared_calibration_scope": plan_pins[
  2388	                    "declared_calibration_scope"
  2389	                ],
  2390	                "relative_path": relative_plan,
  2391	                "sha256": plan_pins["sha256"],
  2392	            },
  2393	            "mint_tool_version": V2_MINT_TOOL_VERSION,
  2394	            "implementation": {
  2395	                "project_commit": project_commit,
  2396	                "project_tree_state": project_tree_state,
  2397	                "python_package": "joulewise",
  2398	            },
  2399	        },
  2400	        cells=[cell],
  2401	        transport_groups=[group],
  2402	    )
  2403	    if artifact["cells"][0]["floor_gate_j"] != group["composed_floor_gate_j"]:
  2404	        raise MintError("v2 post-construction transport headline mismatch")
  2405	    errors = core.validate_floor_artifact(artifact)
  2406	    if errors:
  2407	        raise MintError(f"constructed v2 cell artifact is invalid: {errors[0]}")
  2408	    core._assert_path_independent(artifact)
  2409	    return artifact
  2410	
  2411	
  2412	def _build_v2_artifacts(
  2413	    *,
  2414	    pinset: V2Pinset,
  2415	    pinset_path: Path,
  2416	    pinset_sha256: str,
  2417	    producer_inputs: Mapping[str, V2ProducerInputs],
  2418	    calibration_ledger_snapshot: Any,
  2419	    project_commit: str,
  2420	    project_tree_state: str,
  2421	) -> tuple[Mapping[str, Any], tuple[Mapping[str, Any], ...]]:
  2422	    """Build the combined artifact and its two deterministic components.
  2423	
  2424	    This helper deliberately does not compare the supplied producer/component
  2425	    hashes; it is the deterministic authoring primitive used to freeze those
  2426	    hashes.  The public mint entry point performs every comparison before it
  2427	    returns an artifact.
  2428	    """
  2429	
  2430	    if re.fullmatch(r"[0-9a-f]{40}", project_commit) is None:
  2431	        raise MintError("project_commit must be 40 lowercase hex chars")
  2432	    if project_tree_state not in {"clean", "dirty"}:
  2433	        raise MintError("project_tree_state must be 'clean' or 'dirty'")
  2434	    component_artifacts: list[Mapping[str, Any]] = []
  2435	    all_cells: list[Mapping[str, Any]] = []
  2436	    all_groups: list[Mapping[str, Any]] = []
  2437	    producer_plan_records: list[Mapping[str, Any]] = []
  2438	
  2439	    for producer_index, producer in enumerate(pinset.value["producer_plans"]):
  2440	        plan_pins = producer["plan"]
  2441	        plan_id = plan_pins["plan_id"]
  2442	        inputs = producer_inputs.get(plan_id)
  2443	        if inputs is None:
  2444	            raise MintError(f"missing authenticated producer inputs for {plan_id!r}")
  2445	        if set(inputs.cells) != {"decode", "prefill"}:
  2446	            raise MintError(
  2447	                f"producer inputs for {plan_id!r} must contain decode and prefill"
  2448	            )
  2449	        if inputs.plan.get("plan_id") != plan_id:
  2450	            raise MintError(f"producer {plan_id!r}: calibration plan identity mismatch")
  2451	        _v2_gate_producer_inventory(producer, inputs)
  2452	        producer_cells: list[Mapping[str, Any]] = []
  2453	        producer_groups: list[Mapping[str, Any]] = []
  2454	        for cell_index, cell_pins in enumerate(producer["cells"]):
  2455	            role = cell_pins["role"]
  2456	            cell_inputs = inputs.cells[role]
  2457	            _v2_gate_component(
  2458	                cell_inputs.absolute,
  2459	                cell_pins["absolute"],
  2460	                label=f"producer[{producer_index}].{role}.absolute",
  2461	                metric=cell_pins["metric"],
  2462	                window_class=cell_pins["window_class"],
  2463	            )
  2464	            _v2_gate_component(
  2465	                cell_inputs.comparative,
  2466	                cell_pins["comparative"],
  2467	                label=f"producer[{producer_index}].{role}.comparative",
  2468	                metric=cell_pins["metric"],
  2469	                window_class=cell_pins["window_class"],
  2470	            )
  2471	            _v2_gate_postcollection(
  2472	                producer=producer,
  2473	                cell_pins=cell_pins,
  2474	                cell_inputs=cell_inputs,
  2475	                producer_inputs=inputs,
  2476	                ledger_snapshot=calibration_ledger_snapshot,
  2477	            )
  2478	            configured_pins = _v2_mint_pinset(producer, cell_pins)
  2479	            core = _configured_core(
  2480	                configured_pins,
  2481	                pinset_path=pinset_path,
  2482	                expected_pinset_sha256=pinset_sha256,
  2483	            )
  2484	            try:
  2485	                cell_artifact = _mint_v2_cell_artifact(
  2486	                    core=core,
  2487	                    producer=producer,
  2488	                    cell_pins=cell_pins,
  2489	                    plan=inputs.plan,
  2490	                    absolute=cell_inputs.absolute,
  2491	                    comparative=cell_inputs.comparative,
  2492	                    project_commit=project_commit,
  2493	                    project_tree_state=project_tree_state,
  2494	                )
  2495	            except core.MintError as exc:
  2496	                raise MintError(str(exc)) from exc
  2497	            cell = copy.deepcopy(cell_artifact["cells"][0])
  2498	            group = copy.deepcopy(cell_artifact["transport_groups"][0])
  2499	            allowed = _v2_allowed_families(
  2500	                cell_inputs.allowed_consumer_condition_families,
  2501	                cell_pins["allowed_consumer_condition_families"],
  2502	                label=f"producer[{producer_index}].cells[{cell_index}].allowlist",
  2503	            )
  2504	            group["allowed_consumer_condition_families"] = allowed
  2505	            producer_cells.append(cell)
  2506	            producer_groups.append(group)
  2507	
  2508	        first_cell_artifact = cell_artifact
  2509	        component = {
  2510	            **copy.deepcopy(first_cell_artifact),
  2511	            "artifact_id": producer["component_artifact"]["artifact_id"],
  2512	            "cells": producer_cells,
  2513	            "transport_groups": producer_groups,
  2514	        }
  2515	        component_errors = validate_floor_artifact(
  2516	            artifact=component,
  2517	            pinset_path=pinset_path,
  2518	            pinset_sha256=pinset_sha256,
  2519	            _skip_v2_hash_binding=True,
  2520	        )
  2521	        if component_errors:
  2522	            raise MintError(
  2523	                f"constructed v2 component artifact is invalid: {component_errors[0]}"
  2524	            )
  2525	        component_artifacts.append(component)
  2526	        all_cells.extend(copy.deepcopy(producer_cells))
  2527	        all_groups.extend(copy.deepcopy(producer_groups))
  2528	        producer_plan_records.append(
  2529	            {
  2530	                "plan_id": plan_id,
  2531	                "declared_calibration_scope": plan_pins[
  2532	                    "declared_calibration_scope"
  2533	                ],
  2534	                "relative_path": plan_pins["relative_path"],
  2535	                "sha256": plan_pins["sha256"],
  2536	            }
  2537	        )
  2538	
  2539	    aggregate = pinset.value["aggregate"]
  2540	    implementation = copy.deepcopy(
  2541	        component_artifacts[0]["provenance"]["implementation"]
  2542	    )
  2543	    artifact = {
  2544	        **copy.deepcopy(component_artifacts[0]),
  2545	        "artifact_id": aggregate["artifact_id"],
  2546	        "calibration_scope": aggregate["calibration_scope"],
  2547	        "source_class": aggregate["source_class"],
  2548	        "provenance": {
  2549	            "calibration_plan": {
  2550	                "plan_id": aggregate["plan_set_id"],
  2551	                "declared_calibration_scope": "production_window",
  2552	                "relative_path": Path(pinset_path).name,
  2553	                "sha256": aggregate["producer_set_sha256"],
  2554	            },
  2555	            "producer_calibration_plans": producer_plan_records,
  2556	            "mint_tool_version": V2_MINT_TOOL_VERSION,
  2557	            "implementation": implementation,
  2558	        },
  2559	        "cells": all_cells,
  2560	        "transport_groups": all_groups,
  2561	    }
  2562	    errors = validate_floor_artifact(
  2563	        artifact=artifact,
  2564	        pinset_path=pinset_path,
  2565	        pinset_sha256=pinset_sha256,
  2566	        _skip_v2_hash_binding=True,
  2567	    )
  2568	    if errors:
  2569	        raise MintError(f"constructed v2 aggregate artifact is invalid: {errors[0]}")
  2570	    return artifact, tuple(component_artifacts)
  2571	
  2572	
  2573	def _validate_v2_artifact_binding(
  2574	    artifact: Mapping[str, Any],
  2575	    pinset: V2Pinset,
  2576	) -> list[str]:
  2577	    errors: list[str] = []
  2578	    value = pinset.value
  2579	    aggregate = value["aggregate"]
  2580	    try:
  1620	                )
  1621	        self.assertEqual(len(artifact["cells"]), 4)
  1622	
  1623	    def test_fabricated_postcollection_pins_refuse_after_self_hash_repair(
  1624	        self,
  1625	    ) -> None:
  1626	        with tempfile.TemporaryDirectory() as tmp:
  1627	            root = Path(tmp)
  1628	            path, _digest, inputs, ledger_snapshot = (
  1629	                freeze_synthetic_v2_pinset(root)
  1630	            )
  1631	            fabricated = load_json(path)
  1632	            custody_hashes = (
  1633	                "pre_receipt_sha256",
  1634	                "pre_content_sha256",
  1635	                "post_receipt_sha256",
  1636	                "post_content_sha256",
  1637	                "bracket_binding_sha256",
  1638	                "terminal_ledger_head_sha256",
  1639	                "extraction_report_sha256",
  1640	            )
  1641	            for producer_index, producer in enumerate(
  1642	                fabricated["producer_plans"]
  1643	            ):
  1644	                for cell in producer["cells"]:
  1645	                    post = cell["postcollection"]
  1646	                    for hash_index, field in enumerate(custody_hashes):
  1647	                        post[field] = format(
  1648	                            producer_index * len(custody_hashes)
  1649	                            + hash_index
  1650	                            + 1,
  1651	                            "x",
  1652	                        ) * 64
  1653	                    post["observed_drift_s"] = "0.012000"
  1654	                    post["applied_allowance_s"] = "0.012000"
  1655	            _repair_v2_pinset_self_hashes(fabricated)
  1656	            candidate_path, candidate_digest = write_pinset(root, fabricated)
  1657	            with self.assertRaisesRegex(
  1658	                generalized.MintError,
  1659	                "postcollection_evidence_mismatch",
  1660	            ):
  1661	                generalized.mint_multi_cell_authenticated_artifact(
  1662	                    pinset_path=candidate_path,
  1663	                    pinset_sha256=candidate_digest,
  1664	                    producer_inputs=inputs,
  1665	                    calibration_ledger_snapshot=ledger_snapshot,
  1666	                    project_commit="0" * 40,
  1667	                    project_tree_state="clean",
  1668	                )
  1669	
  1670	    def test_floor_rendering_and_extraction_record_mismatches_refuse(self) -> None:
  1671	        with tempfile.TemporaryDirectory() as tmp:
  1672	            root = Path(tmp)
  1673	            path, _digest, inputs, ledger_snapshot = (
  1674	                freeze_synthetic_v2_pinset(root)
  1675	            )
  1676	            source = load_json(path)
  1677	            for field, replacement, message in (
  1678	                (
  1679	                    "absolute_floor_six_decimal",
  1680	                    "6.294381",
  1681	                    r"absolute_floor\.six_decimal must equal the \.6f rendering",
  1682	                ),
  1683	                (
  1684	                    "comparative_floor_six_decimal",
  1685	                    "13.998036",
  1686	                    r"comparative_floor\.six_decimal must equal the \.6f rendering",
  1687	                ),
  1688	                (
  1689	                    "operative_floor_six_decimal",
  1690	                    "13.998036",
  1691	                    r"operative_floor\.six_decimal must equal the \.6f rendering",
  1692	                ),
  1693	                (
  1694	                    "absolute_floor_full_precision",
  1695	                    "6.294380135190099",
  1696	                    "absolute_floor_full_precision mismatch",
  1697	                ),
  1698	            ):
  1699	                with self.subTest(field=field):
  1700	                    candidate = copy.deepcopy(source)
  1701	                    candidate["producer_plans"][0]["cells"][0][
  1702	                        "postcollection"
  1703	                    ][field] = replacement
  1704	                    _repair_v2_pinset_self_hashes(candidate)
  1705	                    candidate_path, candidate_digest = write_pinset(
  1706	                        root, candidate
  1707	                    )
  1708	                    with self.assertRaisesRegex(
  1709	                        generalized.MintError,
  1710	                        message,
  1711	                    ):
  1712	                        generalized.mint_multi_cell_authenticated_artifact(
  1713	                            pinset_path=candidate_path,
  1714	                            pinset_sha256=candidate_digest,
  1715	                            producer_inputs=inputs,
  1716	                            calibration_ledger_snapshot=ledger_snapshot,
  1717	                            project_commit="0" * 40,
  1718	                            project_tree_state="clean",
  1719	                        )
  1720	
  1721	    def test_coordinated_report_and_pin_change_refuses_against_floor_evidence(
  1722	        self,
  1723	    ) -> None:
  1724	        with tempfile.TemporaryDirectory() as tmp:
  1725	            root = Path(tmp)
  1726	            path, _digest, inputs, ledger_snapshot = (
  1727	                freeze_synthetic_v2_pinset(root)
  1728	            )
  1729	            candidate = load_json(path)
  1730	            producer = candidate["producer_plans"][0]
  1731	            decode_post = producer["cells"][0]["postcollection"]
  1732	            decode_post["absolute_floor_full_precision"] = "6.294381135190098"
  1733	            decode_post["absolute_floor_six_decimal"] = "6.294381"
  1734	
  1735	            plan_id = producer["plan"]["plan_id"]
  1736	            source = inputs[plan_id]
  1737	            report = copy.deepcopy(source.cells["decode"].absolute.report)
  1738	            report_row = next(
  1739	                row
  1740	                for row in report["floor_mint_postcollection"]["cells"]
  1741	                if row["cell_id"] == producer["cells"][0]["cell_id"]
  1742	            )
  1743	            report_row["absolute_floor_full_precision"] = (
  1744	                "6.294381135190098"
  1745	            )
  1746	            report_row["absolute_floor_six_decimal"] = "6.294381"
  1747	            report_sha256 = _fixture_artifact_sha256(report)
  1748	            for cell_pin in producer["cells"]:
  1749	                cell_pin["postcollection"]["extraction_report_sha256"] = (
  1750	                    report_sha256
  1751	                )
  1752	            updated_cells = {
  1753	                role: generalized.V2CellComponents(
  1754	                    absolute=replace(
  1755	                        cell.absolute,
  1756	                        report=report,
  1757	                        report_sha256=report_sha256,
  1758	                    ),
  1759	                    comparative=replace(
  1760	                        cell.comparative,
  1761	                        report=report,
  1762	                        report_sha256=report_sha256,
  1763	                    ),
  1764	                    allowed_consumer_condition_families=(
  1765	                        cell.allowed_consumer_condition_families
  1766	                    ),
  1767	                )
  1768	                for role, cell in source.cells.items()
  1769	            }
  1770	            coordinated_inputs = {
  1771	                **inputs,
  1772	                plan_id: replace(source, cells=updated_cells),
  1773	            }
  1774	            _repair_v2_pinset_self_hashes(candidate)
  1775	            candidate_path, candidate_digest = write_pinset(root, candidate)
  1776	            with self.assertRaisesRegex(
  1777	                generalized.MintError,
  1778	                "absolute full-precision value mismatch",
  1779	            ):
  1780	                generalized.mint_multi_cell_authenticated_artifact(
  1781	                    pinset_path=candidate_path,
  1782	                    pinset_sha256=candidate_digest,
  1783	                    producer_inputs=coordinated_inputs,
  1784	                    calibration_ledger_snapshot=ledger_snapshot,
  1785	                    project_commit="0" * 40,
  1786	                    project_tree_state="clean",
  1787	                )
  1788	
  1789	    def test_per_component_consumption_semantics_pin_is_evidence_bound(
  1790	        self,
  1791	    ) -> None:
  1792	        with tempfile.TemporaryDirectory() as tmp:
  1793	            root = Path(tmp)
  1794	            path, _digest, inputs, ledger_snapshot = (
  1795	                freeze_synthetic_v2_pinset(root)
  1796	            )
  1797	            candidate = load_json(path)
  1798	            candidate["producer_plans"][0]["cells"][0]["absolute"][
  1799	                "consumption_semantics_id"
  1800	            ] = MINTED_CONSUMPTION_SEMANTICS_ID
  1801	            _repair_v2_pinset_self_hashes(candidate)
  1802	            candidate_path, candidate_digest = write_pinset(root, candidate)
  1803	            with self.assertRaisesRegex(
  1804	                generalized.MintError,
  1805	                "consumption semantics mismatch",
  1880	                        "--single-count-out",
  1881	                        str(root / "single-count.txt"),
  1882	                        "--project-commit",
  1883	                        "0" * 40,
  1884	                        "--project-tree-state",
  1885	                        "clean",
  1886	                    ]
  1887	                )
  1888	            self.assertEqual(exit_code, 2)
  1889	            self.assertIn("requires --v2-input-manifest", stderr.getvalue())
  1890	
  1891	    def test_production_cli_mints_and_names_every_custody_mismatch(self) -> None:
  1892	        with tempfile.TemporaryDirectory() as tmp:
  1893	            root = Path(tmp)
  1894	            pinset_path, pinset_sha256, manifest_path, load_test_core = (
  1895	                install_v2_cli_fixture(root)
  1896	            )
  1897	            source = load_json(pinset_path)
  1898	
  1899	            def cli_args(label: str, path: Path, digest: str) -> list[str]:
  1900	                return [
  1901	                    "--pinset",
  1902	                    str(path),
  1903	                    "--pinset-sha256",
  1904	                    digest,
  1905	                    "--v2-input-manifest",
  1906	                    str(manifest_path),
  1907	                    "--out",
  1908	                    str(root / f"{label}-floor.json"),
  1909	                    "--single-count-out",
  1910	                    str(root / f"{label}-single-count.txt"),
  1911	                    "--project-commit",
  1912	                    "0" * 40,
  1913	                    "--project-tree-state",
  1914	                    "clean",
  1915	                ]
  1916	
  1917	            with mock.patch.object(
  1918	                generalized,
  1919	                "_fresh_original_core",
  1920	                side_effect=load_test_core,
  1921	            ):
  1922	                self.assertEqual(
  1923	                    generalized.main(
  1924	                        cli_args("correct", pinset_path, pinset_sha256)
  1925	                    ),
  1926	                    0,
  1927	                )
  1928	            self.assertTrue((root / "correct-floor.json").is_file())
  1929	            self.assertTrue((root / "correct-single-count.txt").is_file())
  1930	
  1931	            mismatch_values = {
  1932	                "pre_receipt_sha256": "0" * 64,
  1933	                "pre_content_sha256": "0" * 64,
  1934	                "post_receipt_sha256": "0" * 64,
  1935	                "post_content_sha256": "0" * 64,
  1936	                "bracket_binding_sha256": "0" * 64,
  1937	                "terminal_ledger_head_sha256": "0" * 64,
  1938	                "extraction_report_sha256": "0" * 64,
  1939	                "observed_drift_s": "0.002000",
  1940	                # Decimal-equivalent spelling preserves the never-zero rule
  1941	                # while still testing exact report-string authentication.
  1942	                "applied_allowance_s": "0.0108180",
  1943	            }
  1944	            for field, replacement in mismatch_values.items():
  1945	                with self.subTest(field=field):
  1946	                    candidate = copy.deepcopy(source)
  1947	                    for cell in candidate["producer_plans"][0]["cells"]:
  1948	                        cell["postcollection"][field] = replacement
  1949	                    _repair_v2_pinset_self_hashes(candidate)
  1950	                    candidate_path, candidate_digest = write_pinset(
  1951	                        root, candidate
  1952	                    )
  1953	                    stderr = io.StringIO()
  1954	                    with (
  1955	                        mock.patch.object(
  1956	                            generalized,
  1957	                            "_fresh_original_core",
  1958	                            side_effect=load_test_core,
  1959	                        ),
  1960	                        mock.patch("sys.stderr", stderr),
  1961	                    ):
  1962	                        exit_code = generalized.main(
  1963	                            cli_args(field, candidate_path, candidate_digest)
  1964	                        )
  1965	                    self.assertEqual(exit_code, 2)
  1966	                    self.assertIn(field, stderr.getvalue())
  1967	                    self.assertFalse((root / f"{field}-floor.json").exists())
  1968	                    self.assertFalse(
  1969	                        (root / f"{field}-single-count.txt").exists()
  1970	                    )
  1971	
  1972	    def test_v2_input_manifest_routes_all_authenticated_evidence_files(
  1973	        self,
  1974	    ) -> None:
  1975	        pinset, source_inputs, ledger_snapshot = synthetic_v2_fixture()
  1976	        with tempfile.TemporaryDirectory() as tmp:
  1977	            root = Path(tmp)
  1978	            acceptance = next(iter(source_inputs.values())).calibration_acceptance
  1979	            acceptance_path = root / "acceptance.json"
  1980	            acceptance_path.write_text(

2026-08-07T20:23:07.498131Z ERROR codex_models_manager::manager: failed to renew cache TTL: missing field `base_instructions` at line 94 column 5
codex
The round-2 code now contains explicit named comparisons for all nine requested custody values. I am separating that result from the deeper trust-anchor question: the ledger path has a committed-head and custody-verification anchor, while report and binding bytes are operator-selected but are cross-validated against that ledger and the source bundles rather than accepted solely because the pinset names them. I’m now probing whether any coordinated mutation can evade the later reconstructed-artifact checks.
exec
/bin/zsh -lc "nl -ba tests/test_mint_floor_artifact_generalized.py | sed -n '1070,1410p'; nl -ba tests/test_mint_floor_artifact_generalized.py | sed -n '1970,2175p'; git show --format= --no-ext-diff HEAD -- scripts/mint_floor_artifact_generalized.py tests/test_mint_floor_artifact_generalized.py scripts/floor_mint_pinsets/schema_v2.json | sed -n '1,240p'" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u3
 succeeded in 0ms:
  1070	    }
  1071	    ledger_snapshot = SimpleNamespace(
  1072	        valid=True,
  1073	        ledger_schema="joulewise.calibration_observation_ledger.v1",
  1074	        receipts=tuple(ledger_receipts),
  1075	        observations=tuple(ledger_observations),
  1076	        bracket_session_by_id=ledger_sessions,
  1077	        head_sequence=len(ledger_receipts),
  1078	        head_digest=ledger_receipts[-1]["receipt_digest"],
  1079	    )
  1080	    return pinset, inputs, ledger_snapshot
  1081	
  1082	
  1083	# Independent golden constants. They are regenerated only by an explicit
  1084	# fixture-review step, never by the mint implementation under test.
  1085	SYNTHETIC_COMPONENT_SHA256S = (
  1086	    "b0404c15df0b2e0afb445ab6cea9b2c08a7922e3d49fd7354b8aec05262d9851",
  1087	    "0543bb0d1282f84e78e6b7c03cc6eaf3903d470bcb58bf39cb9d63fda5922fef",
  1088	)
  1089	SYNTHETIC_PRODUCER_PIN_SHA256S = (
  1090	    "70e3c43269a2bdd4bfc651d136086b6b0b863c8a4f9de1a1716d81d879c44a8b",
  1091	    "e1f600ebbae32be565abdb64098d5c4046f101f041ea5bd8f7c2800b7f6a4278",
  1092	)
  1093	SYNTHETIC_PRODUCER_SET_SHA256 = (
  1094	    "f58ed63311a5e62a1b61dc9c43c653c0caddc5aa201ae17533a28eabaa397c11"
  1095	)
  1096	CLI_COMPONENT_SHA256S = (
  1097	    "77ec1d85330f48773f6f597cdff3df891a5382df0a7685d3e0ebc0c9555ef9b8",
  1098	    "6b586ce5e430daa7defc88cadbd7dc05132dc401366f81272d40f2c8591f5c3f",
  1099	)
  1100	
  1101	
  1102	def _repair_v2_pinset_self_hashes(pinset: dict) -> None:
  1103	    """Repair only pinset self-hashes with an independent JSON oracle."""
  1104	
  1105	    for producer, entry in zip(
  1106	        pinset["producer_plans"],
  1107	        pinset["aggregate"]["component_artifacts"],
  1108	    ):
  1109	        entry["producer_pin_sha256"] = _fixture_canonical_sha256(producer)
  1110	    pinset["aggregate"]["producer_set_sha256"] = _fixture_canonical_sha256(
  1111	        pinset["producer_plans"]
  1112	    )
  1113	
  1114	
  1115	def freeze_synthetic_v2_pinset(
  1116	    root: Path,
  1117	) -> tuple[
  1118	    Path,
  1119	    str,
  1120	    dict[str, generalized.V2ProducerInputs],
  1121	    SimpleNamespace,
  1122	]:
  1123	    pinset, inputs, ledger_snapshot = synthetic_v2_fixture()
  1124	    for producer, entry, component_sha256, producer_sha256 in zip(
  1125	        pinset["producer_plans"],
  1126	        pinset["aggregate"]["component_artifacts"],
  1127	        SYNTHETIC_COMPONENT_SHA256S,
  1128	        SYNTHETIC_PRODUCER_PIN_SHA256S,
  1129	    ):
  1130	        producer["component_artifact"]["sha256"] = component_sha256
  1131	        entry["sha256"] = component_sha256
  1132	        entry["producer_pin_sha256"] = producer_sha256
  1133	    pinset["aggregate"]["producer_set_sha256"] = (
  1134	        SYNTHETIC_PRODUCER_SET_SHA256
  1135	    )
  1136	    path, digest = write_pinset(root, pinset)
  1137	    return path, digest, inputs, ledger_snapshot
  1138	
  1139	
  1140	def install_v2_cli_fixture(root: Path):
  1141	    """Install file-backed v2 inputs and a narrow v1-core test adapter."""
  1142	
  1143	    pinset, source_inputs, _source_snapshot = synthetic_v2_fixture()
  1144	    acceptance = next(iter(source_inputs.values())).calibration_acceptance
  1145	    acceptance_path = root / "acceptance.json"
  1146	    acceptance_path.write_text(
  1147	        json.dumps(acceptance, indent=2, sort_keys=True) + "\n",
  1148	        encoding="utf-8",
  1149	    )
  1150	    acceptance_sha256 = file_sha256(acceptance_path)
  1151	    ledger_path = root / "ledger.jsonl"
  1152	    ledger_path.write_text("{}\n", encoding="utf-8")
  1153	    head_path = root / "ledger.head.json"
  1154	    head_path.write_text("{}\n", encoding="utf-8")
  1155	
  1156	    component_by_source = {}
  1157	    manifest_producers = []
  1158	    ledger_receipts = []
  1159	    ledger_observations = []
  1160	    ledger_sessions = {}
  1161	    for producer_index, producer in enumerate(pinset["producer_plans"]):
  1162	        plan_id = producer["plan"]["plan_id"]
  1163	        source = source_inputs[plan_id]
  1164	        plan_path = root / f"{plan_id}.json"
  1165	        plan_path.write_text(
  1166	            json.dumps(source.plan, indent=2, sort_keys=True) + "\n",
  1167	            encoding="utf-8",
  1168	        )
  1169	        plan_sha256 = file_sha256(plan_path)
  1170	        sidecar_path = root / f"{plan_id}.sha256"
  1171	        sidecar_path.write_text(
  1172	            f"{plan_sha256}  {plan_path.name}\n",
  1173	            encoding="utf-8",
  1174	        )
  1175	        producer["plan"].update(
  1176	            {
  1177	                "sha256": plan_sha256,
  1178	                "declared_sha256": plan_sha256,
  1179	                "sidecar_sha256": file_sha256(sidecar_path),
  1180	            }
  1181	        )
  1182	        producer["calibration_acceptance"]["artifact_sha256"] = (
  1183	            acceptance_sha256
  1184	        )
  1185	
  1186	        evidence_root = root / f"{plan_id}-root"
  1187	        evidence_root.mkdir()
  1188	        binding, receipts, observations, session = _synthetic_bracket_evidence(
  1189	            producer_index,
  1190	            plan_id=plan_id,
  1191	            plan_sha256=plan_sha256,
  1192	            evidence_root_id=producer["evidence_root_id"],
  1193	            runs_root=evidence_root,
  1194	            sequence_start=1 + 3 * producer_index,
  1195	        )
  1196	        ledger_receipts.extend(receipts)
  1197	        ledger_observations.extend(observations)
  1198	        ledger_sessions[session.session_id] = session
  1199	        binding_path = root / f"{plan_id}.binding.json"
  1200	        binding_path.write_text(
  1201	            json.dumps(binding, indent=2, sort_keys=True) + "\n",
  1202	            encoding="utf-8",
  1203	        )
  1204	        binding_sha256 = file_sha256(binding_path)
  1205	
  1206	        role_inputs = {}
  1207	        manifest_cells = []
  1208	        for cell_pin in producer["cells"]:
  1209	            role = cell_pin["role"]
  1210	            source_cell = source.cells[role]
  1211	            components = {}
  1212	            component_paths = {}
  1213	            for component_name, source_component in (
  1214	                ("absolute", source_cell.absolute),
  1215	                ("comparative", source_cell.comparative),
  1216	            ):
  1217	                label = f"{plan_id}-{role}-{component_name}"
  1218	                report_path = root / f"{label}-report.json"
  1219	                report_path.write_text(
  1220	                    json.dumps(
  1221	                        source_component.report,
  1222	                        indent=2,
  1223	                        sort_keys=True,
  1224	                    )
  1225	                    + "\n",
  1226	                    encoding="utf-8",
  1227	                )
  1228	                spec_path = root / f"{label}-spec.json"
  1229	                spec_path.write_text(
  1230	                    json.dumps(
  1231	                        source_component.spec,
  1232	                        indent=2,
  1233	                        sort_keys=True,
  1234	                    )
  1235	                    + "\n",
  1236	                    encoding="utf-8",
  1237	                )
  1238	                order = {
  1239	                    **source_component.order_manifest,
  1240	                    "calibration_plan_sha256": plan_sha256,
  1241	                }
  1242	                order_path = root / f"{label}-order.json"
  1243	                order_path.write_text(
  1244	                    json.dumps(order, indent=2, sort_keys=True) + "\n",
  1245	                    encoding="utf-8",
  1246	                )
  1247	                component = replace(
  1248	                    source_component,
  1249	                    report_sha256=file_sha256(report_path),
  1250	                    spec_sha256=file_sha256(spec_path),
  1251	                    order_manifest=order,
  1252	                    order_manifest_sha256=file_sha256(order_path),
  1253	                )
  1254	                components[component_name] = component
  1255	                component_paths[component_name] = {
  1256	                    "evidence_root": str(evidence_root),
  1257	                    "report": str(report_path),
  1258	                    "spec": str(spec_path),
  1259	                    "order_manifest": str(order_path),
  1260	                }
  1261	                component_by_source[
  1262	                    (
  1263	                        component.calibration_cell_id,
  1264	                        str(evidence_root.resolve()),
  1265	                    )
  1266	                ] = component
  1267	                cell_pin[component_name] = _v2_component_pin(component)
  1268	            cell_pin["postcollection"] = _v2_postcollection(
  1269	                components["absolute"],
  1270	                components["comparative"],
  1271	                bracket_binding=binding,
  1272	                bracket_binding_sha256=binding_sha256,
  1273	                extraction_report_sha256=components[
  1274	                    "absolute"
  1275	                ].report_sha256,
  1276	            )
  1277	            role_inputs[role] = generalized.V2CellComponents(
  1278	                absolute=components["absolute"],
  1279	                comparative=components["comparative"],
  1280	                allowed_consumer_condition_families=(
  1281	                    source_cell.allowed_consumer_condition_families
  1282	                ),
  1283	            )
  1284	            manifest_cells.append(
  1285	                {
  1286	                    "role": role,
  1287	                    **component_paths,
  1288	                    "allowed_consumer_condition_families": list(
  1289	                        source_cell.allowed_consumer_condition_families
  1290	                    ),
  1291	                }
  1292	            )
  1293	        components = [
  1294	            component
  1295	            for role_input in role_inputs.values()
  1296	            for component in (role_input.absolute, role_input.comparative)
  1297	        ]
  1298	        producer["extraction_spec"].update(
  1299	            {
  1300	                "sha256": components[0].spec_sha256,
  1301	                "member_count": len(
  1302	                    {
  1303	                        member_row.bundle_id
  1304	                        for component in components
  1305	                        for member_row in component.members
  1306	                    }
  1307	                ),
  1308	            }
  1309	        )
  1310	        manifest_producers.append(
  1311	            {
  1312	                "plan_id": plan_id,
  1313	                "calibration_plan": str(plan_path),
  1314	                "calibration_plan_sidecar": str(sidecar_path),
  1315	                "bracket_binding": str(binding_path),
  1316	                "cells": manifest_cells,
  1317	            }
  1318	        )
  1319	
  1320	    ledger_snapshot = SimpleNamespace(
  1321	        valid=True,
  1322	        ledger_schema="joulewise.calibration_observation_ledger.v1",
  1323	        receipts=tuple(ledger_receipts),
  1324	        observations=tuple(ledger_observations),
  1325	        bracket_session_by_id=ledger_sessions,
  1326	        head_sequence=len(ledger_receipts),
  1327	        head_digest=ledger_receipts[-1]["receipt_digest"],
  1328	    )
  1329	    manifest_path = root / "manifest.json"
  1330	    manifest_path.write_text(
  1331	        json.dumps(
  1332	            {
  1333	                "schema_version": "joulewise.floor_mint_inputs.v2",
  1334	                "calibration_acceptance": str(acceptance_path),
  1335	                "calibration_ledger": str(ledger_path),
  1336	                "calibration_ledger_head_pin": str(head_path),
  1337	                "producer_plans": manifest_producers,
  1338	            },
  1339	            indent=2,
  1340	            sort_keys=True,
  1341	        )
  1342	        + "\n",
  1343	        encoding="utf-8",
  1344	    )
  1345	
  1346	    original_core_loader = generalized._fresh_original_core
  1347	
  1348	    def load_test_core():
  1349	        core = original_core_loader()
  1350	
  1351	        def load_acceptance(path):
  1352	            if Path(path).read_bytes() != acceptance_path.read_bytes():
  1353	                return None
  1354	            return acceptance
  1355	
  1356	        def authenticate(paths, **kwargs):
  1357	            source_key = (
  1358	                paths.calibration_cell_id,
  1359	                str(paths.evidence_root.resolve()),
  1360	            )
  1361	            expected = component_by_source.get(source_key)
  1362	            if expected is None:
  1363	                raise core.MintError("unexpected component cell/evidence root")
  1364	            for path, expected_sha256 in (
  1365	                (paths.report_path, expected.report_sha256),
  1366	                (paths.spec_path, expected.spec_sha256),
  1367	                (paths.order_manifest_path, expected.order_manifest_sha256),
  1368	            ):
  1369	                if file_sha256(path) != expected_sha256:
  1370	                    raise core.MintError("component artifact bytes mismatch")
  1371	            if kwargs.get("expected_basis_sha256") != (
  1372	                expected.whole_window_evaluation_basis_sha256
  1373	            ):
  1374	                raise core.MintError("component basis dispatch mismatch")
  1375	            if kwargs.get("expected_consumption_semantics_id") != (
  1376	                expected.consumption_semantics_id
  1377	            ):
  1378	                raise core.MintError("component semantics dispatch mismatch")
  1379	            if kwargs.get("calibration_ledger_snapshot") is not ledger_snapshot:
  1380	                raise core.MintError("component ledger snapshot identity mismatch")
  1381	            return expected
  1382	
  1383	        core.load_calibration_acceptance_bound = load_acceptance
  1384	        core.load_calibration_ledger_snapshot = lambda **_kwargs: ledger_snapshot
  1385	        core._authenticate_component = authenticate
  1386	        core.bind_floor_artifact_evidence = lambda *_args, **_kwargs: {}
  1387	        return core
  1388	
  1389	    for producer, entry, component_sha256 in zip(
  1390	        pinset["producer_plans"],
  1391	        pinset["aggregate"]["component_artifacts"],
  1392	        CLI_COMPONENT_SHA256S,
  1393	    ):
  1394	        producer["component_artifact"]["sha256"] = component_sha256
  1395	        entry["sha256"] = component_sha256
  1396	    _repair_v2_pinset_self_hashes(pinset)
  1397	    pinset_path, pinset_sha256 = write_pinset(root, pinset)
  1398	    return pinset_path, pinset_sha256, manifest_path, load_test_core
  1399	
  1400	
  1401	class PinsetTests(unittest.TestCase):
  1402	    def test_mint1_pinset_is_exactly_the_original_hard_pin_set(self) -> None:
  1403	        pinset = generalized.load_pinset(
  1404	            MINT1_PINSET, file_sha256(MINT1_PINSET)
  1405	        )
  1406	        self.assertEqual(pinset.plan.sha256, mint1.PLAN_SHA256)
  1407	        self.assertEqual(pinset.artifact.cell_id, mint1.CELL_ID)
  1408	        self.assertEqual(
  1409	            pinset.absolute.evaluation_basis_sha256,
  1410	            mint1.A10_EVALUATION_BASIS_SHA256,
  1970	                    )
  1971	
  1972	    def test_v2_input_manifest_routes_all_authenticated_evidence_files(
  1973	        self,
  1974	    ) -> None:
  1975	        pinset, source_inputs, ledger_snapshot = synthetic_v2_fixture()
  1976	        with tempfile.TemporaryDirectory() as tmp:
  1977	            root = Path(tmp)
  1978	            acceptance = next(iter(source_inputs.values())).calibration_acceptance
  1979	            acceptance_path = root / "acceptance.json"
  1980	            acceptance_path.write_text(
  1981	                json.dumps(acceptance, indent=2, sort_keys=True) + "\n",
  1982	                encoding="utf-8",
  1983	            )
  1984	            acceptance_sha256 = file_sha256(acceptance_path)
  1985	            ledger_path = root / "ledger.jsonl"
  1986	            ledger_path.write_text("{}\n", encoding="utf-8")
  1987	            head_path = root / "ledger.head.json"
  1988	            head_path.write_text("{}\n", encoding="utf-8")
  1989	            component_by_cell_id = {}
  1990	            expected_report_text = {}
  1991	            manifest_producers = []
  1992	            for producer, component_sha256 in zip(
  1993	                pinset["producer_plans"], SYNTHETIC_COMPONENT_SHA256S
  1994	            ):
  1995	                producer["component_artifact"]["sha256"] = component_sha256
  1996	                plan_id = producer["plan"]["plan_id"]
  1997	                source = source_inputs[plan_id]
  1998	                plan_path = root / f"{plan_id}.json"
  1999	                plan_path.write_text(
  2000	                    json.dumps(source.plan, indent=2, sort_keys=True) + "\n",
  2001	                    encoding="utf-8",
  2002	                )
  2003	                plan_sha256 = file_sha256(plan_path)
  2004	                declared_sha256 = plan_sha256
  2005	                sidecar_path = root / f"{plan_id}.sha256"
  2006	                sidecar_path.write_text(
  2007	                    f"{declared_sha256}  {plan_path.name}\n",
  2008	                    encoding="utf-8",
  2009	                )
  2010	                producer["plan"].update(
  2011	                    {
  2012	                        "sha256": plan_sha256,
  2013	                        "declared_sha256": declared_sha256,
  2014	                        "sidecar_sha256": file_sha256(sidecar_path),
  2015	                    }
  2016	                )
  2017	                producer["calibration_acceptance"][
  2018	                    "artifact_sha256"
  2019	                ] = acceptance_sha256
  2020	                binding = copy.deepcopy(source.bracket_binding)
  2021	                binding["plan_sha256"] = plan_sha256
  2022	                producer_evidence_root = root / f"{plan_id}-root"
  2023	                producer_evidence_root.mkdir()
  2024	                binding["runs_root"] = str(
  2025	                    producer_evidence_root.resolve(strict=False)
  2026	                )
  2027	                binding["binding_digest"] = _fixture_canonical_sha256(
  2028	                    {
  2029	                        key: value
  2030	                        for key, value in binding.items()
  2031	                        if key != "binding_digest"
  2032	                    }
  2033	                )
  2034	                binding_path = root / f"{plan_id}.binding.json"
  2035	                binding_path.write_text(
  2036	                    json.dumps(binding, indent=2, sort_keys=True) + "\n",
  2037	                    encoding="utf-8",
  2038	                )
  2039	                binding_sha256 = file_sha256(binding_path)
  2040	                manifest_cells = []
  2041	                for cell_pin in producer["cells"]:
  2042	                    role = cell_pin["role"]
  2043	                    source_cell = source.cells[role]
  2044	                    component_rows = {}
  2045	                    for component_name, component in (
  2046	                        ("absolute", source_cell.absolute),
  2047	                        ("comparative", source_cell.comparative),
  2048	                    ):
  2049	                        label = f"{plan_id}-{role}-{component_name}"
  2050	                        paths = {
  2051	                            "evidence_root": str(producer_evidence_root),
  2052	                            "report": str(root / f"{label}-report.json"),
  2053	                            "spec": str(root / f"{label}-spec.json"),
  2054	                            "order_manifest": str(root / f"{label}-order.json"),
  2055	                        }
  2056	                        for field in ("report", "spec", "order_manifest"):
  2057	                            Path(paths[field]).write_text(
  2058	                                f"{component.calibration_cell_id}:{field}\n",
  2059	                                encoding="utf-8",
  2060	                            )
  2061	                        component_rows[component_name] = paths
  2062	                        component_by_cell_id[
  2063	                            component.calibration_cell_id
  2064	                        ] = component
  2065	                        expected_report_text[
  2066	                            component.calibration_cell_id
  2067	                        ] = Path(paths["report"]).read_text(encoding="utf-8")
  2068	                    cell_pin["postcollection"][
  2069	                        "bracket_binding_sha256"
  2070	                    ] = binding_sha256
  2071	                    manifest_cells.append(
  2072	                        {
  2073	                            "role": role,
  2074	                            **component_rows,
  2075	                            "allowed_consumer_condition_families": list(
  2076	                                source_cell.allowed_consumer_condition_families
  2077	                            ),
  2078	                        }
  2079	                    )
  2080	                manifest_producers.append(
  2081	                    {
  2082	                        "plan_id": plan_id,
  2083	                        "calibration_plan": str(plan_path),
  2084	                        "calibration_plan_sidecar": str(sidecar_path),
  2085	                        "bracket_binding": str(binding_path),
  2086	                        "cells": manifest_cells,
  2087	                    }
  2088	                )
  2089	            for entry, component_sha256 in zip(
  2090	                pinset["aggregate"]["component_artifacts"],
  2091	                SYNTHETIC_COMPONENT_SHA256S,
  2092	            ):
  2093	                entry["sha256"] = component_sha256
  2094	            _repair_v2_pinset_self_hashes(pinset)
  2095	            pinset_path, pinset_sha256 = write_pinset(root, pinset)
  2096	            loaded = generalized.load_pinset(pinset_path, pinset_sha256)
  2097	            manifest = {
  2098	                "schema_version": "joulewise.floor_mint_inputs.v2",
  2099	                "calibration_acceptance": str(acceptance_path),
  2100	                "calibration_ledger": str(ledger_path),
  2101	                "calibration_ledger_head_pin": str(head_path),
  2102	                "producer_plans": manifest_producers,
  2103	            }
  2104	            manifest_path = root / "manifest.json"
  2105	            manifest_path.write_text(
  2106	                json.dumps(manifest, indent=2, sort_keys=True) + "\n",
  2107	                encoding="utf-8",
  2108	            )
  2109	
  2110	            evidence_core = SimpleNamespace(
  2111	                load_calibration_acceptance_bound=mock.Mock(
  2112	                    return_value=acceptance
  2113	                ),
  2114	                load_calibration_ledger_snapshot=mock.Mock(
  2115	                    return_value=ledger_snapshot
  2116	                ),
  2117	            )
  2118	
  2119	            def authenticate(paths, **kwargs):
  2120	                expected = component_by_cell_id[paths.calibration_cell_id]
  2121	                self.assertEqual(
  2122	                    paths.report_path.read_text(encoding="utf-8"),
  2123	                    expected_report_text[paths.calibration_cell_id],
  2124	                )
  2125	                self.assertEqual(
  2126	                    kwargs["expected_consumption_semantics_id"],
  2127	                    expected.consumption_semantics_id,
  2128	                )
  2129	                self.assertIs(
  2130	                    kwargs["calibration_ledger_snapshot"], ledger_snapshot
  2131	                )
  2132	                return expected
  2133	
  2134	            component_core = SimpleNamespace(
  2135	                MintError=mint1.MintError,
  2136	                ComponentPaths=mint1.ComponentPaths,
  2137	                _authenticate_component=mock.Mock(side_effect=authenticate),
  2138	            )
  2139	            with (
  2140	                mock.patch.object(
  2141	                    generalized,
  2142	                    "_fresh_original_core",
  2143	                    return_value=evidence_core,
  2144	                ),
  2145	                mock.patch.object(
  2146	                    generalized,
  2147	                    "_configured_core",
  2148	                    return_value=component_core,
  2149	                ),
  2150	            ):
  2151	                authenticated, roots, observed_snapshot = (
  2152	                    generalized._authenticate_v2_inputs(
  2153	                        pinset=loaded,
  2154	                        pinset_path=pinset_path,
  2155	                        pinset_sha256=pinset_sha256,
  2156	                        input_manifest_path=manifest_path,
  2157	                        strict_validator=lambda _path, _strict: [],
  2158	                        consumption_semantics_id=None,
  2159	                    )
  2160	                )
  2161	        self.assertEqual(set(authenticated), set(source_inputs))
  2162	        self.assertEqual(len(roots), 2)
  2163	        self.assertIs(observed_snapshot, ledger_snapshot)
  2164	        self.assertEqual(component_core._authenticate_component.call_count, 8)
  2165	        evidence_core.load_calibration_acceptance_bound.assert_called_once_with(
  2166	            acceptance_path
  2167	        )
  2168	        evidence_core.load_calibration_ledger_snapshot.assert_called_once()
  2169	
  2170	    def test_missing_unresolved_and_derived_literal_attempts_refuse(self) -> None:
  2171	        with tempfile.TemporaryDirectory() as tmp:
  2172	            root = Path(tmp)
  2173	            path, _digest, _inputs, _snapshot = freeze_synthetic_v2_pinset(root)
  2174	            source = load_json(path)
  2175	            cases = {}
diff --git a/scripts/floor_mint_pinsets/schema_v2.json b/scripts/floor_mint_pinsets/schema_v2.json
index cc3c77a..39705f8 100644
--- a/scripts/floor_mint_pinsets/schema_v2.json
+++ b/scripts/floor_mint_pinsets/schema_v2.json
@@ -398,7 +398,7 @@
       }
     },
     "finalPostcollection": {
-      "description": "Every field is authenticated at mint: ledger receipt/content and terminal-head pins against the ledger snapshot and bracket binding; drift, allowance, full-precision values, and six-decimal renderings by exact string equality against the authenticated extraction report. The mint never renders a six-decimal value.",
+      "description": "Every field is authenticated by named equality checks at mint. Receipt/content pins are read from authenticated ledger observations, the terminal head from the authenticated bracket binding and ledger chain, bracket-binding and extraction-report hashes from the exact supplied artifact bytes, and observed drift/applied allowance plus floor values/renderings from the authenticated extraction report. Each six-decimal literal must also equal Decimal ROUND_HALF_EVEN .6f semantics for its full-precision pin; the mint verifies that relationship without producing or replacing the supplied literal.",
       "type": "object",
       "additionalProperties": false,
       "required": [
diff --git a/scripts/mint_floor_artifact_generalized.py b/scripts/mint_floor_artifact_generalized.py
index 34cf745..5dc2f10 100644
--- a/scripts/mint_floor_artifact_generalized.py
+++ b/scripts/mint_floor_artifact_generalized.py
@@ -22,7 +22,7 @@ import re
 import stat
 import sys
 from dataclasses import dataclass, replace
-from decimal import Decimal, InvalidOperation
+from decimal import Decimal, InvalidOperation, ROUND_HALF_EVEN, localcontext
 from pathlib import Path
 from types import ModuleType
 from typing import Any, Callable, Mapping, Sequence
@@ -56,6 +56,7 @@ _ORIGINAL_MINT_PATH = Path(__file__).with_name("mint_floor_artifact.py")
 _SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
 _DECIMAL_RE = re.compile(r"^(?:0|[1-9][0-9]*)(?:\.[0-9]+)?$")
 _SIX_DECIMAL_RE = re.compile(r"^(?:0|[1-9][0-9]*)\.[0-9]{6}$")
+_SIX_DECIMAL_QUANTUM = Decimal("0.000001")
 _EVIDENCE_ROOT_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
 _SEMANTICS_IDS = {
     MINTED_CONSUMPTION_SEMANTICS_ID,
@@ -352,6 +353,29 @@ def _six_decimal(value: object, label: str) -> str:
     return value
 
 
+def _verify_six_decimal_rendering(
+    full_precision: object,
+    six_decimal: object,
+    *,
+    label: str,
+) -> None:
+    """Verify Decimal ``.6f`` semantics without rendering a mint literal."""
+
+    full = _decimal_text(full_precision, f"{label}.full_precision")
+    literal = _six_decimal(six_decimal, f"{label}.six_decimal")
+    with localcontext() as context:
+        context.prec = max(80, len(full.as_tuple().digits) + 7)
+        rounded = full.quantize(
+            _SIX_DECIMAL_QUANTUM,
+            rounding=ROUND_HALF_EVEN,
+        )
+    if Decimal(literal) != rounded:
+        raise MintError(
+            f"{label}.six_decimal must equal the .6f rendering of "
+            f"{label}.full_precision"
+        )
+
+
 def _member_pins(value: object, label: str) -> tuple[tuple[str, str], ...]:
     if not isinstance(value, list) or not value:
         raise MintError(f"{label} must be a nonempty array")
@@ -555,6 +579,12 @@ def _parse_v2_postcollection(value: object, label: str) -> None:
         "operative_floor_six_decimal",
     ):
         _six_decimal(row[name], f"{label}.{name}")
+    for component_name in ("absolute", "comparative", "operative"):
+        _verify_six_decimal_rendering(
+            row[f"{component_name}_floor_full_precision"],
+            row[f"{component_name}_floor_six_decimal"],
+            label=f"{label}.{component_name}_floor",
+        )
     if operative_full != max(absolute_full, comparative_full):
         raise MintError(
             f"{label}.operative_floor_full_precision must equal the armwise maximum, never a sum"
@@ -1663,6 +1693,19 @@ def _mapping_attribute(value: object, name: str) -> object:
     return getattr(value, name, None)
 
 
+def _require_postcollection_evidence_equal(
+    field: str,
+    pinned: object,
+    evidenced: object,
+    *,
+    source: str,
+) -> None:
+    if pinned != evidenced:
+        raise MintError(
+            f"postcollection_evidence_mismatch: {field} mismatch against {source}"
+        )
+
+
 def _v2_extraction_postcollection_record(
     component: Any,
     cell_id: str,
@@ -1724,6 +1767,12 @@ def _v2_extraction_postcollection_record(
         "operative_floor_six_decimal",
     ):
         _six_decimal(row[name], f"{label}.{name}")
+    for component_name in ("absolute", "comparative", "operative"):
+        _verify_six_decimal_rendering(
+            row[f"{component_name}_floor_full_precision"],
+            row[f"{component_name}_floor_six_decimal"],
+            label=f"{label}.{component_name}_floor",
+        )
     return row
 
 
@@ -2018,29 +2067,37 @@ def _v2_gate_postcollection(
         ledger_snapshot=ledger_snapshot,
     )
     expected_binding_sha256 = post["bracket_binding_sha256"]
-    if producer_inputs.bracket_binding_sha256 != expected_binding_sha256:
-        raise MintError(
-            "postcollection_evidence_mismatch: bracket-binding artifact sha256 mismatch"
-        )
+    _require_postcollection_evidence_equal(
+        "bracket_binding_sha256",
+        expected_binding_sha256,
+        producer_inputs.bracket_binding_sha256,
+        source="supplied bracket-binding artifact bytes",
+    )
     binding = producer_inputs.bracket_binding
-    endpoint_pins = {
-        "pre": (post["pre_receipt_sha256"], post["pre_content_sha256"]),
-        "post": (post["post_receipt_sha256"], post["post_content_sha256"]),
+    endpoint_fields = {
+        "pre": ("pre_receipt_sha256", "pre_content_sha256"),
+        "post": ("post_receipt_sha256", "post_content_sha256"),
     }
     for role, observation in (("pre", pre), ("post", post_observation)):
-        if endpoint_pins[role] != (
+        receipt_field, content_field = endpoint_fields[role]
+        _require_postcollection_evidence_equal(
+            receipt_field,
+            post[receipt_field],
             _mapping_attribute(observation, "receipt_digest"),
+            source=f"authenticated ledger {role} observation",
+        )
+        _require_postcollection_evidence_equal(
+            content_field,
+            post[content_field],
             _mapping_attribute(observation, "content_id"),
-        ):
-            raise MintError(
-                f"postcollection_evidence_mismatch: {role} receipt/content pin mismatch"
-            )
-    if post["terminal_ledger_head_sha256"] != binding["terminal_head"][
-        "head_digest"
-    ]:
-        raise MintError(
-            "postcollection_evidence_mismatch: terminal ledger head pin mismatch"
+            source=f"authenticated ledger {role} observation",
         )
+    _require_postcollection_evidence_equal(
+        "terminal_ledger_head_sha256",
+        post["terminal_ledger_head_sha256"],
+        binding["terminal_head"]["head_digest"],
+        source="authenticated bracket-binding terminal head",
+    )
     try:
         observed_drift = abs(
             _decimal_text(
@@ -2056,18 +2113,19 @@ def _v2_gate_postcollection(
         raise MintError(
             "postcollection_evidence_mismatch: ledger endpoint drift is not exact Decimal evidence"
         ) from exc
-    if observed_drift != _decimal_text(
-        post["observed_drift_s"], "postcollection.observed_drift_s"
-    ):
-        raise MintError(
-            "postcollection_evidence_mismatch: observed drift pin mismatch"
-        )
+    _require_postcollection_evidence_equal(
+        "observed_drift_s",
+        _decimal_text(post["observed_drift_s"], "postcollection.observed_drift_s"),
+        observed_drift,
+        source="authenticated ledger endpoint bounds",
+    )
     actual_components = (cell_inputs.absolute, cell_inputs.comparative)
-    if {component.report_sha256 for component in actual_components} != {
-        post["extraction_report_sha256"]
-    }:
-        raise MintError(
-            "postcollection_evidence_mismatch: extraction-report sha256 mismatch"
+    for component in actual_components:
+        _require_postcollection_evidence_equal(
+            "extraction_report_sha256",
+            post["extraction_report_sha256"],
+            component.report_sha256,
+            source=f"supplied {component.kind} extraction-report artifact bytes",
         )
     records = [
         _v2_extraction_postcollection_record(
@@ -2092,10 +2150,12 @@ def _v2_gate_postcollection(
         "comparative_floor_six_decimal",
         "operative_floor_six_decimal",
     ):
-        if post[name] != report_record[name]:
-            raise MintError(
-                f"postcollection_evidence_mismatch: extraction-recorded {name} mismatch"
-            )
+        _require_postcollection_evidence_equal(
+            name,
+            post[name],
+            report_record[name],
+            source="authenticated extraction-report record",
+        )
     actual_values = (
         cell_inputs.absolute.cell.get("floor", {}).get(
             "drift_widened_guarded_floor_j"
diff --git a/tests/test_mint_floor_artifact_generalized.py b/tests/test_mint_floor_artifact_generalized.py
index a14dc1e..6f34d4a 100644
--- a/tests/test_mint_floor_artifact_generalized.py
+++ b/tests/test_mint_floor_artifact_generalized.py
@@ -1,5 +1,6 @@
 from __future__ import annotations
 
+import ast
 import copy
 import hashlib
 import io
@@ -612,7 +613,7 @@ def _v2_component_pin(component: mint1.AuthenticatedComponent) -> dict:
         "evaluation_basis_members": component.evaluation_basis_member_count,
         "extraction_spec_sha256": component.spec_sha256,
         "extraction_spec_members": len(
-            set(generalized._v2_spec_member_ids(component.spec))
+            set(_fixture_spec_member_ids(component.spec))
         ),
         "expected_n": (
             len(component.members)
@@ -635,6 +636,27 @@ def _v2_component_pin(component: mint1.AuthenticatedComponent) -> dict:
     }
 
 
+def _fixture_spec_member_ids(spec: dict) -> tuple[str, ...]:
+    """Independent physical-member projection for the golden pin fixture."""
+

exec
/bin/zsh -lc "rg -n -C 80 'MINT_SUCCEEDED|actual_report_sha|pinned_report_sha|pinned_pre_receipt_sha' docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-EXEC.md | sed -n '1,260p'; git diff HEAD"'^..HEAD -- scripts/mint_floor_artifact_generalized.py | sed -n '"'1,400p'; git diff HEAD"'^..HEAD -- tests/test_mint_floor_artifact_generalized.py | sed -n '"'1,900p'" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u3
 succeeded in 0ms:
12265-   828	        "schema_version",
12266-   829	        "mint_tool_version",
12267-   830	        "producer_plans",
12268-   831	        "aggregate"
12269-   832	      ],
12270-   833	      "properties": {
12271-   834	        "schema_version": {
12272-   835	          "const": "joulewise.floor_mint_pin_requirements.v2"
12273-   836	        },
12274-   837	        "mint_tool_version": {
12275-   838	          "const": "joulewise.floor_mint.generalized.v2"
12276-   839	        },
12277-   840	        "producer_plans": {
12278-   841	          "type": "array",
12279-   842	          "minItems": 2,
12280-   843	          "maxItems": 2,
12281-   844	          "items": {
12282-   845	            "$ref": "#/$defs/deskProducer"
12283-   846	          }
12284-   847	        },
12285-   848	        "aggregate": {
12286-   849	          "$ref": "#/$defs/deskAggregate"
12287-   850	        }
12288-   851	      }
12289-   852	    },
12290-   853	    "finalPinset": {
12291-   854	      "type": "object",
12292-   855	      "additionalProperties": false,
12293-   856	      "required": [
12294-   857	        "schema_version",
12295-   858	        "mint_tool_version",
12296-   859	        "producer_plans",
12297-   860	        "aggregate"
12298-   861	      ],
12299-   862	      "properties": {
12300-   863	        "schema_version": {
12301-   864	          "const": "joulewise.floor_mint_pinset.v2"
12302-   865	        },
12303-   866	        "mint_tool_version": {
12304-   867	          "const": "joulewise.floor_mint.generalized.v2"
12305-   868	        },
12306-   869	        "producer_plans": {
12307-   870	          "type": "array",
12308-   871	          "minItems": 2,
12309-   872	          "maxItems": 2,
12310-   873	          "items": {
12311-   874	            "$ref": "#/$defs/finalProducer"
12312-   875	          }
12313-   876	        },
12314-   877	        "aggregate": {
12315-   878	          "$ref": "#/$defs/finalAggregate"
12316-   879	        }
12317-   880	      }
12318-   881	    }
12319-   882	  }
12320-   883	}
12321-jsonschema unavailable: ModuleNotFoundError No module named 'jsonschema'
12322-
12323-exec
12324-/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/joulewise-audit-pycache python3 - <<'PY'
12325-import copy, tempfile
12326-from pathlib import Path
12327-from tests.test_mint_floor_artifact_generalized import freeze_synthetic_v2_pinset, load_json, write_pinset
12328-from scripts import mint_floor_artifact_generalized as g
12329-with tempfile.TemporaryDirectory(dir='/tmp') as tmp:
12330-    root = Path(tmp)
12331-    path, _digest, inputs = freeze_synthetic_v2_pinset(root)
12332-    candidate = load_json(path)
12333-    pinned = candidate['aggregate']['transport_allowlists'][0]['allowed_consumer_condition_families'][0]
12334-    pinned['condition_family_id'] = 'aggregate-only-family'
12335-    pinned['condition_family_sha256'] = 'a' * 64
12336-    mutated_path, mutated_digest = write_pinset(root, candidate)
12337-    artifact = g.mint_multi_cell_authenticated_artifact(
12338-        pinset_path=mutated_path,
12339-        pinset_sha256=mutated_digest,
12340-        producer_inputs=inputs,
12341-        project_commit='0' * 40,
12342-        project_tree_state='clean',
12343-    )
12344-    emitted = artifact['transport_groups'][0]['allowed_consumer_condition_families'][0]
12345:    print('MINT_SUCCEEDED')
12346-    print('aggregate_pin=', pinned['condition_family_id'], pinned['condition_family_sha256'])
12347-    print('emitted_group=', emitted['condition_family_id'], emitted['condition_family_sha256'])
12348-    print('validator_errors=', g.validate_floor_artifact(artifact=artifact, pinset_path=mutated_path, pinset_sha256=mutated_digest))
12349-PY" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u3
12350- succeeded in 707ms:
12351:MINT_SUCCEEDED
12352-aggregate_pin= aggregate-only-family aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
12353-emitted_group= synthetic-0-decode b0a5cdb0d48edb16a33cc57081ada00b87e4ff2ab9d28a0f20d94d10d39f84cf
12354-validator_errors= []
12355-
12356-exec
12357-/bin/zsh -lc "nl -ba scripts/mint_floor_artifact_generalized.py | sed -n '1235,1388p' && rg -n \"validate_floor_artifact\\(\" --glob '*.py' | head -n 80 && rg -n \"producer_calibration_plans|family_identities|_project_floor_mint_pinset_v2\" tests" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u3
12358- exited 1 in 0ms:
12359-  1235	                order_manifest=order_manifest,
12360-  1236	            )
12361-  1237	
12362-  1238	        original_gate(
12363-  1239	            plan=normalized_plan,
12364-  1240	            plan_sha256=plan_sha256,
12365-  1241	            absolute=normalized_component(absolute, "a10"),
12366-  1242	            comparative=normalized_component(comparative, "window_c"),
12367-  1243	        )
12368-  1244	
12369-  1245	    core.pre_registration_gate = generalized_gate
12370-  1246	    return core
12371-  1247	
12372-  1248	
12373-  1249	def pre_registration_gate(
12374-  1250	    *,
12375-  1251	    pinset_path: Path,
12376-  1252	    pinset_sha256: str,
12377-  1253	    plan: Mapping[str, Any],
12378-  1254	    plan_sha256: str,
12379-  1255	    absolute: Any,
12380-  1256	    comparative: Any,
12381-  1257	) -> None:
12382-  1258	    """Run the configured pre-registration gate without building an artifact."""
12383-  1259	
12384-  1260	    pinset = _load_v1_pinset(pinset_path, pinset_sha256)
12385-  1261	    core = _configured_core(
12386-  1262	        pinset,
12387-  1263	        pinset_path=pinset_path,
12388-  1264	        expected_pinset_sha256=pinset_sha256,
12389-  1265	    )
12390-  1266	    try:
12391-  1267	        core.pre_registration_gate(
12392-  1268	            plan=plan,
12393-  1269	            plan_sha256=plan_sha256,
12394-  1270	            absolute=absolute,
12395-  1271	            comparative=comparative,
12396-  1272	        )
12397-  1273	    except core.MintError as exc:
12398-  1274	        raise MintError(str(exc)) from exc
12399-  1275	
12400-  1276	
12401-  1277	def mint_authenticated_artifact(
12402-  1278	    *,
12403-  1279	    pinset_path: Path,
12404-  1280	    pinset_sha256: str,
12405-  1281	    artifact_id: str,
12406-  1282	    plan: Mapping[str, Any],
12407-  1283	    plan_sha256: str,
12408-  1284	    calibration_plan_relative_path: str,
12409-  1285	    absolute: Any,
12410-  1286	    comparative: Any,
12411-  1287	    project_commit: str,
12412-  1288	    project_tree_state: str,
12413-  1289	) -> Mapping[str, Any]:
12414-  1290	    """Gate and build from already-authenticated component fixtures/evidence."""
12415-  1291	
12416-  1292	    pinset = _load_v1_pinset(pinset_path, pinset_sha256)
12417-  1293	    core = _configured_core(
12418-  1294	        pinset,
12419-  1295	        pinset_path=pinset_path,
12420-  1296	        expected_pinset_sha256=pinset_sha256,
12421-  1297	    )
12422-  1298	    try:
12423-  1299	        return core.mint_authenticated_artifact(
12424-  1300	            artifact_id=artifact_id,
12425-  1301	            plan=plan,
12426-  1302	            plan_sha256=plan_sha256,
12427-  1303	            calibration_plan_relative_path=calibration_plan_relative_path,
12428-  1304	            absolute=absolute,
12429-  1305	            comparative=comparative,
12430-  1306	            project_commit=project_commit,
12431-  1307	            project_tree_state=project_tree_state,
--
14193-   154	    """All information admitted before the pre-registration gate."""
14194-   155	
14195-   156	    evidence_root_id: str
14196-   157	    calibration_cell_id: str
14197-   158	    kind: str
14198-   159	    report: Mapping[str, Any]
14199-   160	    report_sha256: str
14200-   161	    spec: Mapping[str, Any]
14201-   162	    spec_sha256: str
14202-   163	    order_manifest: Mapping[str, Any]
14203-   164	    order_manifest_sha256: str
14204-   165	    campaign_log_sha256: str
14205-   166	    cell: Mapping[str, Any]
14206-   167	    spec_cell: Mapping[str, Any]
14207-   168	    members: tuple[AuthenticatedMember, ...]
14208-   169	    widths_j: tuple[float, ...]
14209-   170	    whole_window_evaluation_basis_sha256: str
14210-   171	    evaluation_basis_member_count: int
14211-   172	    consumption_semantics_id: str
14212-   173	    whole_window_drift_allowance: Mapping[str, Any]
14213-   174	    source_regime: Mapping[str, Any]
14214-   175	    scientific_config_identity_sha256: str
14215-   176	    backend: str
14216-   177	
14217-   178	
14218-   179	def _sha256(raw: bytes) -> str:
14219-   180	    return hashlib.sha256(raw).hexdigest()
14220-   181	
14221-   182	
14222-   183	def _load_json_object(path: Path, label: str) -> tuple[Mapping[str, Any], bytes]:
14223-   184	    try:
14224-   185	        raw = Path(path).read_bytes()
14225-   186	    except OSError as exc:
14226-   187	        raise MintError(f"{label} cannot be read: {exc}") from exc
14227-   188	    try:
14228-   189	        value = json.loads(raw.decode("utf-8"))
14229-   190	    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
14230-   191	        raise MintError(f"{label} is not valid UTF-8 JSON: {exc}") from exc
14231-   192	    if not isinstance(value, Mapping):
14232-   193	        raise MintError(f"{label} must contain a JSON object")
14233-   194	    return value, raw
14234-   195	
14235-   196	
14236-   197	def _load_json_lines(path: Path, label: str) -> tuple[list[Mapping[str, Any]], bytes]:
14237-   198	    try:
14238-   199	        raw = Path(path).read_bytes()
14239-   200	    except OSError as exc:
14240-   201	        raise MintError(f"{label} cannot be read: {exc}") from exc
14241-   202	    rows: list[Mapping[str, Any]] = []
14242-   203	    try:
14243-   204	        for line in raw.decode("utf-8").splitlines():
14244-   205	            if not line.strip():
14245-   206	                continue
14246-   207	            row = json.loads(line)
14247-   208	            if not isinstance(row, Mapping):
14248-   209	                raise MintError(f"{label} rows must be JSON objects")
14249-   210	            rows.append(row)
14250-   211	    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
14251-   212	        raise MintError(f"{label} is not valid UTF-8 JSONL: {exc}") from exc
14252-   213	    return rows, raw
14253-   214	
14254-   215	
14255-   216	def _finite(value: object, label: str, *, nonnegative: bool = False) -> float:
14256-   217	    if isinstance(value, bool) or not isinstance(value, int | float):
14257-   218	        raise MintError(f"{label} must be a finite number")
14258-   219	    converted = float(value)
14259-   220	    if not math.isfinite(converted) or (nonnegative and converted < 0.0):
14260-
14261-exec
14262-/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/joulewise-audit-pycache python3 - <<'PY'
14263-import tempfile
14264-from pathlib import Path
14265-from tests.test_mint_floor_artifact_generalized import freeze_synthetic_v2_pinset, load_json, write_pinset
14266-from scripts import mint_floor_artifact_generalized as g
14267-with tempfile.TemporaryDirectory(dir='/tmp') as tmp:
14268-    root = Path(tmp)
14269-    path, _digest, inputs = freeze_synthetic_v2_pinset(root)
14270-    candidate = load_json(path)
14271-    producer = candidate['producer_plans'][0]
14272-    cell = producer['cells'][0]
14273:    actual_report_sha = inputs[producer['plan']['plan_id']].cells['decode'].absolute.report_sha256
14274-    cell['postcollection']['extraction_report_sha256'] = '9' * 64
14275-    cell['postcollection']['pre_receipt_sha256'] = '8' * 64
14276-    producer['model_runtime_config']['runtime_identity_sha256'] = '7' * 64
14277-    producer_hashes = [g._canonical_json_sha256(p) for p in candidate['producer_plans']]
14278-    for entry, digest in zip(candidate['aggregate']['component_artifacts'], producer_hashes):
14279-        entry['producer_pin_sha256'] = digest
14280-    candidate['aggregate']['producer_set_sha256'] = g._canonical_json_sha256(candidate['producer_plans'])
14281-    mutated_path, mutated_digest = write_pinset(root, candidate)
14282-    artifact = g.mint_multi_cell_authenticated_artifact(
14283-        pinset_path=mutated_path,
14284-        pinset_sha256=mutated_digest,
diff --git a/scripts/mint_floor_artifact_generalized.py b/scripts/mint_floor_artifact_generalized.py
index 34cf745..5dc2f10 100644
--- a/scripts/mint_floor_artifact_generalized.py
+++ b/scripts/mint_floor_artifact_generalized.py
@@ -22,7 +22,7 @@ import re
 import stat
 import sys
 from dataclasses import dataclass, replace
-from decimal import Decimal, InvalidOperation
+from decimal import Decimal, InvalidOperation, ROUND_HALF_EVEN, localcontext
 from pathlib import Path
 from types import ModuleType
 from typing import Any, Callable, Mapping, Sequence
@@ -56,6 +56,7 @@ _ORIGINAL_MINT_PATH = Path(__file__).with_name("mint_floor_artifact.py")
 _SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
 _DECIMAL_RE = re.compile(r"^(?:0|[1-9][0-9]*)(?:\.[0-9]+)?$")
 _SIX_DECIMAL_RE = re.compile(r"^(?:0|[1-9][0-9]*)\.[0-9]{6}$")
+_SIX_DECIMAL_QUANTUM = Decimal("0.000001")
 _EVIDENCE_ROOT_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
 _SEMANTICS_IDS = {
     MINTED_CONSUMPTION_SEMANTICS_ID,
@@ -352,6 +353,29 @@ def _six_decimal(value: object, label: str) -> str:
     return value
 
 
+def _verify_six_decimal_rendering(
+    full_precision: object,
+    six_decimal: object,
+    *,
+    label: str,
+) -> None:
+    """Verify Decimal ``.6f`` semantics without rendering a mint literal."""
+
+    full = _decimal_text(full_precision, f"{label}.full_precision")
+    literal = _six_decimal(six_decimal, f"{label}.six_decimal")
+    with localcontext() as context:
+        context.prec = max(80, len(full.as_tuple().digits) + 7)
+        rounded = full.quantize(
+            _SIX_DECIMAL_QUANTUM,
+            rounding=ROUND_HALF_EVEN,
+        )
+    if Decimal(literal) != rounded:
+        raise MintError(
+            f"{label}.six_decimal must equal the .6f rendering of "
+            f"{label}.full_precision"
+        )
+
+
 def _member_pins(value: object, label: str) -> tuple[tuple[str, str], ...]:
     if not isinstance(value, list) or not value:
         raise MintError(f"{label} must be a nonempty array")
@@ -555,6 +579,12 @@ def _parse_v2_postcollection(value: object, label: str) -> None:
         "operative_floor_six_decimal",
     ):
         _six_decimal(row[name], f"{label}.{name}")
+    for component_name in ("absolute", "comparative", "operative"):
+        _verify_six_decimal_rendering(
+            row[f"{component_name}_floor_full_precision"],
+            row[f"{component_name}_floor_six_decimal"],
+            label=f"{label}.{component_name}_floor",
+        )
     if operative_full != max(absolute_full, comparative_full):
         raise MintError(
             f"{label}.operative_floor_full_precision must equal the armwise maximum, never a sum"
@@ -1663,6 +1693,19 @@ def _mapping_attribute(value: object, name: str) -> object:
     return getattr(value, name, None)
 
 
+def _require_postcollection_evidence_equal(
+    field: str,
+    pinned: object,
+    evidenced: object,
+    *,
+    source: str,
+) -> None:
+    if pinned != evidenced:
+        raise MintError(
+            f"postcollection_evidence_mismatch: {field} mismatch against {source}"
+        )
+
+
 def _v2_extraction_postcollection_record(
     component: Any,
     cell_id: str,
@@ -1724,6 +1767,12 @@ def _v2_extraction_postcollection_record(
         "operative_floor_six_decimal",
     ):
         _six_decimal(row[name], f"{label}.{name}")
+    for component_name in ("absolute", "comparative", "operative"):
+        _verify_six_decimal_rendering(
+            row[f"{component_name}_floor_full_precision"],
+            row[f"{component_name}_floor_six_decimal"],
+            label=f"{label}.{component_name}_floor",
+        )
     return row
 
 
@@ -2018,29 +2067,37 @@ def _v2_gate_postcollection(
         ledger_snapshot=ledger_snapshot,
     )
     expected_binding_sha256 = post["bracket_binding_sha256"]
-    if producer_inputs.bracket_binding_sha256 != expected_binding_sha256:
-        raise MintError(
-            "postcollection_evidence_mismatch: bracket-binding artifact sha256 mismatch"
-        )
+    _require_postcollection_evidence_equal(
+        "bracket_binding_sha256",
+        expected_binding_sha256,
+        producer_inputs.bracket_binding_sha256,
+        source="supplied bracket-binding artifact bytes",
+    )
     binding = producer_inputs.bracket_binding
-    endpoint_pins = {
-        "pre": (post["pre_receipt_sha256"], post["pre_content_sha256"]),
-        "post": (post["post_receipt_sha256"], post["post_content_sha256"]),
+    endpoint_fields = {
+        "pre": ("pre_receipt_sha256", "pre_content_sha256"),
+        "post": ("post_receipt_sha256", "post_content_sha256"),
     }
     for role, observation in (("pre", pre), ("post", post_observation)):
-        if endpoint_pins[role] != (
+        receipt_field, content_field = endpoint_fields[role]
+        _require_postcollection_evidence_equal(
+            receipt_field,
+            post[receipt_field],
             _mapping_attribute(observation, "receipt_digest"),
+            source=f"authenticated ledger {role} observation",
+        )
+        _require_postcollection_evidence_equal(
+            content_field,
+            post[content_field],
             _mapping_attribute(observation, "content_id"),
-        ):
-            raise MintError(
-                f"postcollection_evidence_mismatch: {role} receipt/content pin mismatch"
-            )
-    if post["terminal_ledger_head_sha256"] != binding["terminal_head"][
-        "head_digest"
-    ]:
-        raise MintError(
-            "postcollection_evidence_mismatch: terminal ledger head pin mismatch"
+            source=f"authenticated ledger {role} observation",
         )
+    _require_postcollection_evidence_equal(
+        "terminal_ledger_head_sha256",
+        post["terminal_ledger_head_sha256"],
+        binding["terminal_head"]["head_digest"],
+        source="authenticated bracket-binding terminal head",
+    )
     try:
         observed_drift = abs(
             _decimal_text(
@@ -2056,18 +2113,19 @@ def _v2_gate_postcollection(
         raise MintError(
             "postcollection_evidence_mismatch: ledger endpoint drift is not exact Decimal evidence"
         ) from exc
-    if observed_drift != _decimal_text(
-        post["observed_drift_s"], "postcollection.observed_drift_s"
-    ):
-        raise MintError(
-            "postcollection_evidence_mismatch: observed drift pin mismatch"
-        )
+    _require_postcollection_evidence_equal(
+        "observed_drift_s",
+        _decimal_text(post["observed_drift_s"], "postcollection.observed_drift_s"),
+        observed_drift,
+        source="authenticated ledger endpoint bounds",
+    )
     actual_components = (cell_inputs.absolute, cell_inputs.comparative)
-    if {component.report_sha256 for component in actual_components} != {
-        post["extraction_report_sha256"]
-    }:
-        raise MintError(
-            "postcollection_evidence_mismatch: extraction-report sha256 mismatch"
+    for component in actual_components:
+        _require_postcollection_evidence_equal(
+            "extraction_report_sha256",
+            post["extraction_report_sha256"],
+            component.report_sha256,
+            source=f"supplied {component.kind} extraction-report artifact bytes",
         )
     records = [
         _v2_extraction_postcollection_record(
@@ -2092,10 +2150,12 @@ def _v2_gate_postcollection(
         "comparative_floor_six_decimal",
         "operative_floor_six_decimal",
     ):
-        if post[name] != report_record[name]:
-            raise MintError(
-                f"postcollection_evidence_mismatch: extraction-recorded {name} mismatch"
-            )
+        _require_postcollection_evidence_equal(
+            name,
+            post[name],
+            report_record[name],
+            source="authenticated extraction-report record",
+        )
     actual_values = (
         cell_inputs.absolute.cell.get("floor", {}).get(
             "drift_widened_guarded_floor_j"
diff --git a/tests/test_mint_floor_artifact_generalized.py b/tests/test_mint_floor_artifact_generalized.py
index a14dc1e..6f34d4a 100644
--- a/tests/test_mint_floor_artifact_generalized.py
+++ b/tests/test_mint_floor_artifact_generalized.py
@@ -1,5 +1,6 @@
 from __future__ import annotations
 
+import ast
 import copy
 import hashlib
 import io
@@ -612,7 +613,7 @@ def _v2_component_pin(component: mint1.AuthenticatedComponent) -> dict:
         "evaluation_basis_members": component.evaluation_basis_member_count,
         "extraction_spec_sha256": component.spec_sha256,
         "extraction_spec_members": len(
-            set(generalized._v2_spec_member_ids(component.spec))
+            set(_fixture_spec_member_ids(component.spec))
         ),
         "expected_n": (
             len(component.members)
@@ -635,6 +636,27 @@ def _v2_component_pin(component: mint1.AuthenticatedComponent) -> dict:
     }
 
 
+def _fixture_spec_member_ids(spec: dict) -> tuple[str, ...]:
+    """Independent physical-member projection for the golden pin fixture."""
+
+    ids: list[str] = []
+    for cell in spec.get("cells", []):
+        if not isinstance(cell, dict):
+            continue
+        for row in cell.get("members", []):
+            if isinstance(row, dict) and isinstance(row.get("bundle_id"), str):
+                ids.append(row["bundle_id"])
+        for block in cell.get("blocks", []):
+            members = block.get("members") if isinstance(block, dict) else None
+            if isinstance(members, dict):
+                ids.extend(
+                    bundle_id
+                    for bundle_id in members.values()
+                    if isinstance(bundle_id, str)
+                )
+    return tuple(ids)
+
+
 def _v2_postcollection(
     absolute: mint1.AuthenticatedComponent,
     comparative: mint1.AuthenticatedComponent,
@@ -1071,6 +1093,10 @@ SYNTHETIC_PRODUCER_PIN_SHA256S = (
 SYNTHETIC_PRODUCER_SET_SHA256 = (
     "f58ed63311a5e62a1b61dc9c43c653c0caddc5aa201ae17533a28eabaa397c11"
 )
+CLI_COMPONENT_SHA256S = (
+    "77ec1d85330f48773f6f597cdff3df891a5382df0a7685d3e0ebc0c9555ef9b8",
+    "6b586ce5e430daa7defc88cadbd7dc05132dc401366f81272d40f2c8591f5c3f",
+)
 
 
 def _repair_v2_pinset_self_hashes(pinset: dict) -> None:
@@ -1111,6 +1137,267 @@ def freeze_synthetic_v2_pinset(
     return path, digest, inputs, ledger_snapshot
 
 
+def install_v2_cli_fixture(root: Path):
+    """Install file-backed v2 inputs and a narrow v1-core test adapter."""
+
+    pinset, source_inputs, _source_snapshot = synthetic_v2_fixture()
+    acceptance = next(iter(source_inputs.values())).calibration_acceptance
+    acceptance_path = root / "acceptance.json"
+    acceptance_path.write_text(
+        json.dumps(acceptance, indent=2, sort_keys=True) + "\n",
+        encoding="utf-8",
+    )
+    acceptance_sha256 = file_sha256(acceptance_path)
+    ledger_path = root / "ledger.jsonl"
+    ledger_path.write_text("{}\n", encoding="utf-8")
+    head_path = root / "ledger.head.json"
+    head_path.write_text("{}\n", encoding="utf-8")
+
+    component_by_source = {}
+    manifest_producers = []
+    ledger_receipts = []
+    ledger_observations = []
+    ledger_sessions = {}
+    for producer_index, producer in enumerate(pinset["producer_plans"]):
+        plan_id = producer["plan"]["plan_id"]
+        source = source_inputs[plan_id]
+        plan_path = root / f"{plan_id}.json"
+        plan_path.write_text(
+            json.dumps(source.plan, indent=2, sort_keys=True) + "\n",
+            encoding="utf-8",
+        )
+        plan_sha256 = file_sha256(plan_path)
+        sidecar_path = root / f"{plan_id}.sha256"
+        sidecar_path.write_text(
+            f"{plan_sha256}  {plan_path.name}\n",
+            encoding="utf-8",
+        )
+        producer["plan"].update(
+            {
+                "sha256": plan_sha256,
+                "declared_sha256": plan_sha256,
+                "sidecar_sha256": file_sha256(sidecar_path),
+            }
+        )
+        producer["calibration_acceptance"]["artifact_sha256"] = (
+            acceptance_sha256
+        )
+
+        evidence_root = root / f"{plan_id}-root"
+        evidence_root.mkdir()
+        binding, receipts, observations, session = _synthetic_bracket_evidence(
+            producer_index,
+            plan_id=plan_id,
+            plan_sha256=plan_sha256,
+            evidence_root_id=producer["evidence_root_id"],
+            runs_root=evidence_root,
+            sequence_start=1 + 3 * producer_index,
+        )
+        ledger_receipts.extend(receipts)
+        ledger_observations.extend(observations)
+        ledger_sessions[session.session_id] = session
+        binding_path = root / f"{plan_id}.binding.json"
+        binding_path.write_text(
+            json.dumps(binding, indent=2, sort_keys=True) + "\n",
+            encoding="utf-8",
+        )
+        binding_sha256 = file_sha256(binding_path)
+
+        role_inputs = {}
+        manifest_cells = []
+        for cell_pin in producer["cells"]:
+            role = cell_pin["role"]
+            source_cell = source.cells[role]
+            components = {}
+            component_paths = {}
+            for component_name, source_component in (
+                ("absolute", source_cell.absolute),
+                ("comparative", source_cell.comparative),
+            ):
+                label = f"{plan_id}-{role}-{component_name}"
+                report_path = root / f"{label}-report.json"
+                report_path.write_text(
+                    json.dumps(
+                        source_component.report,
+                        indent=2,
+                        sort_keys=True,
+                    )
+                    + "\n",
+                    encoding="utf-8",
+                )
+                spec_path = root / f"{label}-spec.json"
+                spec_path.write_text(
+                    json.dumps(
+                        source_component.spec,
+                        indent=2,
+                        sort_keys=True,
+                    )
+                    + "\n",
+                    encoding="utf-8",
+                )
+                order = {
+                    **source_component.order_manifest,
+                    "calibration_plan_sha256": plan_sha256,
+                }
+                order_path = root / f"{label}-order.json"
+                order_path.write_text(
+                    json.dumps(order, indent=2, sort_keys=True) + "\n",
+                    encoding="utf-8",
+                )
+                component = replace(
+                    source_component,
+                    report_sha256=file_sha256(report_path),
+                    spec_sha256=file_sha256(spec_path),
+                    order_manifest=order,
+                    order_manifest_sha256=file_sha256(order_path),
+                )
+                components[component_name] = component
+                component_paths[component_name] = {
+                    "evidence_root": str(evidence_root),
+                    "report": str(report_path),
+                    "spec": str(spec_path),
+                    "order_manifest": str(order_path),
+                }
+                component_by_source[
+                    (
+                        component.calibration_cell_id,
+                        str(evidence_root.resolve()),
+                    )
+                ] = component
+                cell_pin[component_name] = _v2_component_pin(component)
+            cell_pin["postcollection"] = _v2_postcollection(
+                components["absolute"],
+                components["comparative"],
+                bracket_binding=binding,
+                bracket_binding_sha256=binding_sha256,
+                extraction_report_sha256=components[
+                    "absolute"
+                ].report_sha256,
+            )
+            role_inputs[role] = generalized.V2CellComponents(
+                absolute=components["absolute"],
+                comparative=components["comparative"],
+                allowed_consumer_condition_families=(
+                    source_cell.allowed_consumer_condition_families
+                ),
+            )
+            manifest_cells.append(
+                {
+                    "role": role,
+                    **component_paths,
+                    "allowed_consumer_condition_families": list(
+                        source_cell.allowed_consumer_condition_families
+                    ),
+                }
+            )
+        components = [
+            component
+            for role_input in role_inputs.values()
+            for component in (role_input.absolute, role_input.comparative)
+        ]
+        producer["extraction_spec"].update(
+            {
+                "sha256": components[0].spec_sha256,
+                "member_count": len(
+                    {
+                        member_row.bundle_id
+                        for component in components
+                        for member_row in component.members
+                    }
+                ),
+            }
+        )
+        manifest_producers.append(
+            {
+                "plan_id": plan_id,
+                "calibration_plan": str(plan_path),
+                "calibration_plan_sidecar": str(sidecar_path),
+                "bracket_binding": str(binding_path),
+                "cells": manifest_cells,
+            }
+        )
+
+    ledger_snapshot = SimpleNamespace(
+        valid=True,
+        ledger_schema="joulewise.calibration_observation_ledger.v1",
+        receipts=tuple(ledger_receipts),
+        observations=tuple(ledger_observations),
+        bracket_session_by_id=ledger_sessions,
+        head_sequence=len(ledger_receipts),
+        head_digest=ledger_receipts[-1]["receipt_digest"],
+    )
+    manifest_path = root / "manifest.json"
+    manifest_path.write_text(
+        json.dumps(
+            {
+                "schema_version": "joulewise.floor_mint_inputs.v2",
+                "calibration_acceptance": str(acceptance_path),
+                "calibration_ledger": str(ledger_path),
+                "calibration_ledger_head_pin": str(head_path),
+                "producer_plans": manifest_producers,
+            },
+            indent=2,
+            sort_keys=True,
+        )
+        + "\n",
+        encoding="utf-8",
+    )
+
+    original_core_loader = generalized._fresh_original_core
+
+    def load_test_core():
+        core = original_core_loader()
+
+        def load_acceptance(path):
+            if Path(path).read_bytes() != acceptance_path.read_bytes():
+                return None
+            return acceptance
+
+        def authenticate(paths, **kwargs):
+            source_key = (
+                paths.calibration_cell_id,
+                str(paths.evidence_root.resolve()),
+            )
+            expected = component_by_source.get(source_key)
+            if expected is None:
+                raise core.MintError("unexpected component cell/evidence root")
+            for path, expected_sha256 in (
+                (paths.report_path, expected.report_sha256),
+                (paths.spec_path, expected.spec_sha256),
+                (paths.order_manifest_path, expected.order_manifest_sha256),
+            ):
+                if file_sha256(path) != expected_sha256:
+                    raise core.MintError("component artifact bytes mismatch")
+            if kwargs.get("expected_basis_sha256") != (
+                expected.whole_window_evaluation_basis_sha256
+            ):
+                raise core.MintError("component basis dispatch mismatch")
+            if kwargs.get("expected_consumption_semantics_id") != (
+                expected.consumption_semantics_id
+            ):
+                raise core.MintError("component semantics dispatch mismatch")
+            if kwargs.get("calibration_ledger_snapshot") is not ledger_snapshot:
+                raise core.MintError("component ledger snapshot identity mismatch")
+            return expected
+
+        core.load_calibration_acceptance_bound = load_acceptance
+        core.load_calibration_ledger_snapshot = lambda **_kwargs: ledger_snapshot
+        core._authenticate_component = authenticate
+        core.bind_floor_artifact_evidence = lambda *_args, **_kwargs: {}
+        return core
+
+    for producer, entry, component_sha256 in zip(
+        pinset["producer_plans"],
+        pinset["aggregate"]["component_artifacts"],
+        CLI_COMPONENT_SHA256S,
+    ):
+        producer["component_artifact"]["sha256"] = component_sha256
+        entry["sha256"] = component_sha256
+    _repair_v2_pinset_self_hashes(pinset)
+    pinset_path, pinset_sha256 = write_pinset(root, pinset)
+    return pinset_path, pinset_sha256, manifest_path, load_test_core
+
+
 class PinsetTests(unittest.TestCase):
     def test_mint1_pinset_is_exactly_the_original_hard_pin_set(self) -> None:
         pinset = generalized.load_pinset(
@@ -1190,12 +1477,25 @@ class V2PinsetAndMintTests(unittest.TestCase):
     def test_synthetic_hash_oracle_is_literal_and_builder_independent(
         self,
     ) -> None:
-        helper_source = inspect.getsource(freeze_synthetic_v2_pinset)
-        self.assertNotIn("_build_v2_artifacts", helper_source)
-        self.assertNotIn("_artifact_sha256", helper_source)
+        helper_source = "\n".join(
+            inspect.getsource(helper)
+            for helper in (
+                synthetic_v2_fixture,
+                freeze_synthetic_v2_pinset,
+                _repair_v2_pinset_self_hashes,
+                _fixture_spec_member_ids,
+            )
+        )
+        self.assertNotIn("generalized._", helper_source)
+        self.assertNotIn("generalized._build_v2_artifacts", helper_source)
+        self.assertNotIn("generalized._artifact_sha256", helper_source)
         self.assertTrue(
             all(value != "0" * 64 for value in SYNTHETIC_COMPONENT_SHA256S)
         )
+        self.assertTrue(
+            all(value != "0" * 64 for value in SYNTHETIC_PRODUCER_PIN_SHA256S)
+        )
+        self.assertNotEqual(SYNTHETIC_PRODUCER_SET_SHA256, "0" * 64)
 
     def test_desk_stage_is_structurally_disjoint_and_cannot_mint(self) -> None:
         final, _inputs, _ledger_snapshot = synthetic_v2_fixture()
@@ -1279,6 +1579,18 @@ class V2PinsetAndMintTests(unittest.TestCase):
         )
 
     def test_v2_mint_does_not_render_or_round_floor_literals(self) -> None:
+        source_tree = ast.parse(inspect.getsource(generalized))
+        formatted_values = [
+            node
+            for node in ast.walk(source_tree)
+            if isinstance(node, ast.FormattedValue)
+            and node.format_spec is not None
+        ]
+        self.assertEqual(
+            formatted_values,
+            [],
+            "v2 mint contains f-string formatting capable of deriving a literal",
+        )
         with tempfile.TemporaryDirectory() as tmp:
             path, digest, inputs, ledger_snapshot = (
                 freeze_synthetic_v2_pinset(Path(tmp))
@@ -1355,16 +1667,34 @@ class V2PinsetAndMintTests(unittest.TestCase):
                     project_tree_state="clean",
                 )
 
-    def test_extraction_recorded_last_decimal_mismatch_refuses(self) -> None:
+    def test_floor_rendering_and_extraction_record_mismatches_refuse(self) -> None:
         with tempfile.TemporaryDirectory() as tmp:
             root = Path(tmp)
             path, _digest, inputs, ledger_snapshot = (
                 freeze_synthetic_v2_pinset(root)
             )
             source = load_json(path)
-            for field, replacement in (
-                ("absolute_floor_six_decimal", "6.294381"),
-                ("absolute_floor_full_precision", "6.294380135190099"),
+            for field, replacement, message in (
+                (
+                    "absolute_floor_six_decimal",
+                    "6.294381",
+                    r"absolute_floor\.six_decimal must equal the \.6f rendering",
+                ),
+                (
+                    "comparative_floor_six_decimal",
+                    "13.998036",
+                    r"comparative_floor\.six_decimal must equal the \.6f rendering",
+                ),
+                (
+                    "operative_floor_six_decimal",
+                    "13.998036",
+                    r"operative_floor\.six_decimal must equal the \.6f rendering",
+                ),
+                (
+                    "absolute_floor_full_precision",
+                    "6.294380135190099",
+                    "absolute_floor_full_precision mismatch",
+                ),
             ):
                 with self.subTest(field=field):
                     candidate = copy.deepcopy(source)
@@ -1377,7 +1707,7 @@ class V2PinsetAndMintTests(unittest.TestCase):
                     )
                     with self.assertRaisesRegex(
                         generalized.MintError,
-                        f"extraction-recorded {field} mismatch",
+                        message,
                     ):
                         generalized.mint_multi_cell_authenticated_artifact(
                             pinset_path=candidate_path,
@@ -1388,6 +1718,74 @@ class V2PinsetAndMintTests(unittest.TestCase):
                             project_tree_state="clean",
                         )
 
+    def test_coordinated_report_and_pin_change_refuses_against_floor_evidence(
+        self,
+    ) -> None:
+        with tempfile.TemporaryDirectory() as tmp:
+            root = Path(tmp)
+            path, _digest, inputs, ledger_snapshot = (
+                freeze_synthetic_v2_pinset(root)
+            )
+            candidate = load_json(path)
+            producer = candidate["producer_plans"][0]
+            decode_post = producer["cells"][0]["postcollection"]
+            decode_post["absolute_floor_full_precision"] = "6.294381135190098"
+            decode_post["absolute_floor_six_decimal"] = "6.294381"
+
+            plan_id = producer["plan"]["plan_id"]
+            source = inputs[plan_id]
+            report = copy.deepcopy(source.cells["decode"].absolute.report)
+            report_row = next(
+                row
+                for row in report["floor_mint_postcollection"]["cells"]
+                if row["cell_id"] == producer["cells"][0]["cell_id"]
+            )
+            report_row["absolute_floor_full_precision"] = (
+                "6.294381135190098"
+            )
+            report_row["absolute_floor_six_decimal"] = "6.294381"
+            report_sha256 = _fixture_artifact_sha256(report)
+            for cell_pin in producer["cells"]:
+                cell_pin["postcollection"]["extraction_report_sha256"] = (
+                    report_sha256
+                )
+            updated_cells = {
+                role: generalized.V2CellComponents(
+                    absolute=replace(
+                        cell.absolute,
+                        report=report,
+                        report_sha256=report_sha256,
+                    ),
+                    comparative=replace(
+                        cell.comparative,
+                        report=report,
+                        report_sha256=report_sha256,
+                    ),
+                    allowed_consumer_condition_families=(
+                        cell.allowed_consumer_condition_families
+                    ),
+                )
+                for role, cell in source.cells.items()
+            }
+            coordinated_inputs = {
+                **inputs,
+                plan_id: replace(source, cells=updated_cells),
+            }
+            _repair_v2_pinset_self_hashes(candidate)
+            candidate_path, candidate_digest = write_pinset(root, candidate)
+            with self.assertRaisesRegex(
+                generalized.MintError,
+                "absolute full-precision value mismatch",
+            ):
+                generalized.mint_multi_cell_authenticated_artifact(
+                    pinset_path=candidate_path,
+                    pinset_sha256=candidate_digest,
+                    producer_inputs=coordinated_inputs,
+                    calibration_ledger_snapshot=ledger_snapshot,
+                    project_commit="0" * 40,
+                    project_tree_state="clean",
+                )
+
     def test_per_component_consumption_semantics_pin_is_evidence_bound(
         self,
     ) -> None:
@@ -1490,6 +1888,87 @@ class V2PinsetAndMintTests(unittest.TestCase):
             self.assertEqual(exit_code, 2)
             self.assertIn("requires --v2-input-manifest", stderr.getvalue())
 
+    def test_production_cli_mints_and_names_every_custody_mismatch(self) -> None:
+        with tempfile.TemporaryDirectory() as tmp:
+            root = Path(tmp)
+            pinset_path, pinset_sha256, manifest_path, load_test_core = (
+                install_v2_cli_fixture(root)
+            )
+            source = load_json(pinset_path)
+
+            def cli_args(label: str, path: Path, digest: str) -> list[str]:
+                return [
+                    "--pinset",
+                    str(path),
+                    "--pinset-sha256",
+                    digest,
+                    "--v2-input-manifest",
+                    str(manifest_path),
+                    "--out",
+                    str(root / f"{label}-floor.json"),
+                    "--single-count-out",
+                    str(root / f"{label}-single-count.txt"),
+                    "--project-commit",
+                    "0" * 40,
+                    "--project-tree-state",
+                    "clean",
+                ]
+
+            with mock.patch.object(
+                generalized,
+                "_fresh_original_core",
+                side_effect=load_test_core,
+            ):
+                self.assertEqual(
+                    generalized.main(
+                        cli_args("correct", pinset_path, pinset_sha256)
+                    ),
+                    0,
+                )
+            self.assertTrue((root / "correct-floor.json").is_file())
+            self.assertTrue((root / "correct-single-count.txt").is_file())
+
+            mismatch_values = {
+                "pre_receipt_sha256": "0" * 64,
+                "pre_content_sha256": "0" * 64,
+                "post_receipt_sha256": "0" * 64,
+                "post_content_sha256": "0" * 64,
+                "bracket_binding_sha256": "0" * 64,
+                "terminal_ledger_head_sha256": "0" * 64,
+                "extraction_report_sha256": "0" * 64,
+                "observed_drift_s": "0.002000",
+                # Decimal-equivalent spelling preserves the never-zero rule
+                # while still testing exact report-string authentication.
+                "applied_allowance_s": "0.0108180",
+            }
+            for field, replacement in mismatch_values.items():
+                with self.subTest(field=field):
+                    candidate = copy.deepcopy(source)
+                    for cell in candidate["producer_plans"][0]["cells"]:
+                        cell["postcollection"][field] = replacement
+                    _repair_v2_pinset_self_hashes(candidate)
+                    candidate_path, candidate_digest = write_pinset(
+                        root, candidate
+                    )
+                    stderr = io.StringIO()
+                    with (
+                        mock.patch.object(
+                            generalized,
+                            "_fresh_original_core",
+                            side_effect=load_test_core,
+                        ),
+                        mock.patch("sys.stderr", stderr),
+                    ):
+                        exit_code = generalized.main(
+                            cli_args(field, candidate_path, candidate_digest)
+                        )
+                    self.assertEqual(exit_code, 2)
+                    self.assertIn(field, stderr.getvalue())
+                    self.assertFalse((root / f"{field}-floor.json").exists())
+                    self.assertFalse(
+                        (root / f"{field}-single-count.txt").exists()
+                    )
+
     def test_v2_input_manifest_routes_all_authenticated_evidence_files(
         self,
     ) -> None:

exec
/bin/zsh -lc "sed -n '14260,14320p' docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-EXEC.md; git show HEAD"'^:tests/test_mint_floor_artifact_generalized.py | rg -n '"'def freeze_synthetic_v2_pinset|def synthetic_v2_fixture|def _v2_postcollection' -n; git show HEAD"'^:tests/test_mint_floor_artifact_generalized.py | sed -n '"'950,1015p'; git show HEAD"'^:scripts/mint_floor_artifact_generalized.py | nl -ba | sed -n '"'1990,2140p'" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u3
 succeeded in 0ms:

exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/joulewise-audit-pycache python3 - <<'PY'
import tempfile
from pathlib import Path
from tests.test_mint_floor_artifact_generalized import freeze_synthetic_v2_pinset, load_json, write_pinset
from scripts import mint_floor_artifact_generalized as g
with tempfile.TemporaryDirectory(dir='/tmp') as tmp:
    root = Path(tmp)
    path, _digest, inputs = freeze_synthetic_v2_pinset(root)
    candidate = load_json(path)
    producer = candidate['producer_plans'][0]
    cell = producer['cells'][0]
    actual_report_sha = inputs[producer['plan']['plan_id']].cells['decode'].absolute.report_sha256
    cell['postcollection']['extraction_report_sha256'] = '9' * 64
    cell['postcollection']['pre_receipt_sha256'] = '8' * 64
    producer['model_runtime_config']['runtime_identity_sha256'] = '7' * 64
    producer_hashes = [g._canonical_json_sha256(p) for p in candidate['producer_plans']]
    for entry, digest in zip(candidate['aggregate']['component_artifacts'], producer_hashes):
        entry['producer_pin_sha256'] = digest
    candidate['aggregate']['producer_set_sha256'] = g._canonical_json_sha256(candidate['producer_plans'])
    mutated_path, mutated_digest = write_pinset(root, candidate)
    artifact = g.mint_multi_cell_authenticated_artifact(
        pinset_path=mutated_path,
        pinset_sha256=mutated_digest,
        producer_inputs=inputs,
        project_commit='0' * 40,
        project_tree_state='clean',
    )
    print('MINT_SUCCEEDED')
    print('actual_report_sha=', actual_report_sha)
    print('pinned_report_sha=', cell['postcollection']['extraction_report_sha256'])
    print('pinned_pre_receipt_sha=', cell['postcollection']['pre_receipt_sha256'])
    print('pinned_runtime_identity_sha=', producer['model_runtime_config']['runtime_identity_sha256'])
    print('validator_errors=', g.validate_floor_artifact(artifact=artifact, pinset_path=mutated_path, pinset_sha256=mutated_digest))
PY" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u3
 succeeded in 699ms:
MINT_SUCCEEDED
actual_report_sha= 1111111111111111111111111111111111111111111111111111111111111111
pinned_report_sha= 9999999999999999999999999999999999999999999999999999999999999999
pinned_pre_receipt_sha= 8888888888888888888888888888888888888888888888888888888888888888
pinned_runtime_identity_sha= 7777777777777777777777777777777777777777777777777777777777777777
validator_errors= []

exec
/bin/zsh -lc "LC_ALL=C PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/joulewise-audit-pycache python3 - <<'PY'
from scripts import mint_floor_artifact_generalized as g
values = ['-0.000000','0.000000','1.230000','1.23','01.230000','1,230000','1e0','+1.000000']
for value in values:
    try:
        out = g._six_decimal(value, 'literal')
    except Exception as exc:
        print('six', repr(value), 'REFUSE', str(exc))
    else:
        print('six', repr(value), 'ACCEPT', out)
for value in ['-0','-0.000000','0.010818','00.010818','1.0818E-2','+0.010818','0,010818']:
    try:
        out = g._decimal_text(value, 'decimal')
    except Exception as exc:
        print('decimal', repr(value), 'REFUSE', str(exc))
    else:
638:def _v2_postcollection(
809:def synthetic_v2_fixture() -> tuple[
1089:def freeze_synthetic_v2_pinset(
                    "transport_group_id": group_id,
                    "cell_ids": [cell_id],
                    "allowed_consumer_condition_families": allowlist,
                }
            )
        components = [
            component
            for role_input in role_inputs.values()
            for component in (role_input.absolute, role_input.comparative)
        ]
        unique_members = {
            member.bundle_id
            for component in components
            for member in component.members
        }
        runtime_identity_sha256 = components[0].source_regime[
            "stack_identity_sha256"
        ]
        acceptance = {
            "schema_version": "joulewise.calibration_acceptance_bound.v2",
            "acceptance_id": "d079-calibration-acceptance-v2",
            "derivation_sha256": "b" * 64,
        }
        producer = {
            "plan": {
                "plan_id": plan_id,
                "sha256": plan_sha256,
                "declared_sha256": declared_sha256,
                "sidecar_sha256": sidecar_sha256,
                "relative_path": f"plans/{plan_id}.json",
                "declared_calibration_scope": "production_window",
                "artifact_calibration_scope": "production_window",
            },
            "evidence_root_id": evidence_root_id,
            "component_artifact": {
                "artifact_id": f"component-artifact-{producer_index}",
                "sha256": "0" * 64,
            },
            "model_runtime_config": {
                "model_artifact_sha256": components[0].source_regime[
                    "stack_identity"
                ]["model_artifact_sha256"],
                "runtime_identity_sha256": runtime_identity_sha256,
                "config_set_sha256": components[
                    0
                ].scientific_config_identity_sha256,
            },
            "extraction_spec": {
                "sha256": extraction_spec_sha256,
                "member_count": len(unique_members),
            },
            "calibration_acceptance": {
                "acceptance_id": acceptance["acceptance_id"],
                "artifact_sha256": "a" * 64,
                "derivation_sha256": acceptance["derivation_sha256"],
                "derivation_rule_id": acceptance["schema_version"],
            },
            "cells": cell_pins,
        }
        producers.append(producer)
        inputs[plan_id] = generalized.V2ProducerInputs(
            plan=plan,
            cells=role_inputs,
            evidence_root=evidence_root,
            plan_sha256=plan_sha256,
            plan_declared_sha256=declared_sha256,
  1990	    runtime_hashes = {
  1991	        component.source_regime.get("stack_identity_sha256")
  1992	        for component in components
  1993	    }
  1994	    config_hashes = {
  1995	        component.scientific_config_identity_sha256 for component in components
  1996	    }
  1997	    runtime_pins = producer["model_runtime_config"]
  1998	    if model_hashes != {runtime_pins["model_artifact_sha256"]}:
  1999	        raise MintError(f"producer {plan_id!r}: model artifact inventory mismatch")
  2000	    if runtime_hashes != {runtime_pins["runtime_identity_sha256"]}:
  2001	        raise MintError(f"producer {plan_id!r}: runtime identity inventory mismatch")
  2002	    if config_hashes != {runtime_pins["config_set_sha256"]}:
  2003	        raise MintError(f"producer {plan_id!r}: config-set inventory mismatch")
  2004	
  2005	
  2006	def _v2_gate_postcollection(
  2007	    *,
  2008	    producer: Mapping[str, Any],
  2009	    cell_pins: Mapping[str, Any],
  2010	    cell_inputs: V2CellComponents,
  2011	    producer_inputs: V2ProducerInputs,
  2012	    ledger_snapshot: Any,
  2013	) -> None:
  2014	    post = cell_pins["postcollection"]
  2015	    pre, post_observation = _v2_authenticate_bracket_binding(
  2016	        producer=producer,
  2017	        inputs=producer_inputs,
  2018	        ledger_snapshot=ledger_snapshot,
  2019	    )
  2020	    expected_binding_sha256 = post["bracket_binding_sha256"]
  2021	    if producer_inputs.bracket_binding_sha256 != expected_binding_sha256:
  2022	        raise MintError(
  2023	            "postcollection_evidence_mismatch: bracket-binding artifact sha256 mismatch"
  2024	        )
  2025	    binding = producer_inputs.bracket_binding
  2026	    endpoint_pins = {
  2027	        "pre": (post["pre_receipt_sha256"], post["pre_content_sha256"]),
  2028	        "post": (post["post_receipt_sha256"], post["post_content_sha256"]),
  2029	    }
  2030	    for role, observation in (("pre", pre), ("post", post_observation)):
  2031	        if endpoint_pins[role] != (
  2032	            _mapping_attribute(observation, "receipt_digest"),
  2033	            _mapping_attribute(observation, "content_id"),
  2034	        ):
  2035	            raise MintError(
  2036	                f"postcollection_evidence_mismatch: {role} receipt/content pin mismatch"
  2037	            )
  2038	    if post["terminal_ledger_head_sha256"] != binding["terminal_head"][
  2039	        "head_digest"
  2040	    ]:
  2041	        raise MintError(
  2042	            "postcollection_evidence_mismatch: terminal ledger head pin mismatch"
  2043	        )
  2044	    try:
  2045	        observed_drift = abs(
  2046	            _decimal_text(
  2047	                _mapping_attribute(pre, "exact_bound_lexeme_s"),
  2048	                "ledger pre exact_bound_lexeme_s",
  2049	            )
  2050	            - _decimal_text(
  2051	                _mapping_attribute(post_observation, "exact_bound_lexeme_s"),
  2052	                "ledger post exact_bound_lexeme_s",
  2053	            )
  2054	        )
  2055	    except (InvalidOperation, MintError) as exc:
  2056	        raise MintError(
  2057	            "postcollection_evidence_mismatch: ledger endpoint drift is not exact Decimal evidence"
  2058	        ) from exc
  2059	    if observed_drift != _decimal_text(
  2060	        post["observed_drift_s"], "postcollection.observed_drift_s"
  2061	    ):
  2062	        raise MintError(
  2063	            "postcollection_evidence_mismatch: observed drift pin mismatch"
  2064	        )
  2065	    actual_components = (cell_inputs.absolute, cell_inputs.comparative)
  2066	    if {component.report_sha256 for component in actual_components} != {
  2067	        post["extraction_report_sha256"]
  2068	    }:
  2069	        raise MintError(
  2070	            "postcollection_evidence_mismatch: extraction-report sha256 mismatch"
  2071	        )
  2072	    records = [
  2073	        _v2_extraction_postcollection_record(
  2074	            component,
  2075	            cell_pins["cell_id"],
  2076	            label=f"{cell_pins['cell_id']}.{component.kind}",
  2077	        )
  2078	        for component in actual_components
  2079	    ]
  2080	    if records[0] != records[1]:
  2081	        raise MintError(
  2082	            "postcollection_evidence_mismatch: component extraction reports disagree"
  2083	        )
  2084	    report_record = records[0]
  2085	    for name in (
  2086	        "observed_drift_s",
  2087	        "applied_allowance_s",
  2088	        "absolute_floor_full_precision",
  2089	        "comparative_floor_full_precision",
  2090	        "operative_floor_full_precision",
  2091	        "absolute_floor_six_decimal",
  2092	        "comparative_floor_six_decimal",
  2093	        "operative_floor_six_decimal",
  2094	    ):
  2095	        if post[name] != report_record[name]:
  2096	            raise MintError(
  2097	                f"postcollection_evidence_mismatch: extraction-recorded {name} mismatch"
  2098	            )
  2099	    actual_values = (
  2100	        cell_inputs.absolute.cell.get("floor", {}).get(
  2101	            "drift_widened_guarded_floor_j"
  2102	        ),
  2103	        cell_inputs.comparative.cell.get("floor", {}).get(
  2104	            "drift_widened_guarded_floor_j"
  2105	        ),
  2106	    )
  2107	    expected_values = (
  2108	        _decimal_text(
  2109	            post["absolute_floor_full_precision"],
  2110	            "postcollection.absolute_floor_full_precision",
  2111	        ),
  2112	        _decimal_text(
  2113	            post["comparative_floor_full_precision"],
  2114	            "postcollection.comparative_floor_full_precision",
  2115	        ),
  2116	    )
  2117	    for name, actual, expected in zip(
  2118	        ("absolute", "comparative"), actual_values, expected_values
  2119	    ):
  2120	        if isinstance(actual, bool) or not isinstance(actual, int | float):
  2121	            raise MintError(
  2122	                f"postcollection_evidence_mismatch: {name} extraction value is not numeric"
  2123	            )
  2124	        if Decimal(str(actual)) != expected:
  2125	            raise MintError(
  2126	                f"postcollection_evidence_mismatch: {name} full-precision value mismatch"
  2127	            )
  2128	
  2129	
  2130	def _v2_allowed_families(
  2131	    supplied: Sequence[Mapping[str, Any]],
  2132	    pins: Sequence[Mapping[str, Any]],
  2133	    *,
  2134	    label: str,
  2135	) -> list[Mapping[str, Any]]:
  2136	    expected = [
  2137	        (row["condition_family_id"], row["condition_family_sha256"])
  2138	        for row in pins
  2139	    ]
  2140	    observed = []

exec
/bin/zsh -lc 'git show HEAD''^:tests/test_mint_floor_artifact_generalized.py | nl -ba | sed -n '"'620,700p'; git show HEAD"'^:tests/test_mint_floor_artifact_generalized.py | nl -ba | sed -n '"'800,1115p'; git show HEAD"'^:scripts/mint_floor_artifact_generalized.py | nl -ba | sed -n '"'700,870p'; git show HEAD"'^:scripts/mint_floor_artifact_generalized.py | nl -ba | sed -n '"'2380,2505p'" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u3
 succeeded in 0ms:
   620	            else len(component.members) // 4
   621	        ),
   622	        "drift_allowance_j": component.whole_window_drift_allowance[
   623	            "allowance_j"
   624	        ],
   625	        "order_manifest_id": component.order_manifest["manifest_id"],
   626	        "order_manifest_sha256": component.order_manifest_sha256,
   627	        "consumption_semantics_id": component.consumption_semantics_id,
   628	        "members": [
   629	            {
   630	                "bundle_id": member_row.bundle_id,
   631	                "config_sha256": member_row.config_sha256,
   632	            }
   633	            for member_row in component.members
   634	        ],
   635	    }
   636	
   637	
   638	def _v2_postcollection(
   639	    absolute: mint1.AuthenticatedComponent,
   640	    comparative: mint1.AuthenticatedComponent,
   641	    *,
   642	    bracket_binding: dict,
   643	    bracket_binding_sha256: str,
   644	    extraction_report_sha256: str,
   645	) -> dict:
   646	    absolute_full = "6.294380135190098"
   647	    comparative_full = "13.998036715259254"
   648	    return {
   649	        "absolute_evaluation_basis_sha256": (
   650	            absolute.whole_window_evaluation_basis_sha256
   651	        ),
   652	        "absolute_evaluation_basis_members": (
   653	            absolute.evaluation_basis_member_count
   654	        ),
   655	        "comparative_evaluation_basis_sha256": (
   656	            comparative.whole_window_evaluation_basis_sha256
   657	        ),
   658	        "comparative_evaluation_basis_members": (
   659	            comparative.evaluation_basis_member_count
   660	        ),
   661	        "pre_receipt_sha256": bracket_binding["endpoints"]["pre"][
   662	            "receipt_digest"
   663	        ],
   664	        "pre_content_sha256": bracket_binding["endpoints"]["pre"][
   665	            "content_digest"
   666	        ],
   667	        "post_receipt_sha256": bracket_binding["endpoints"]["post"][
   668	            "receipt_digest"
   669	        ],
   670	        "post_content_sha256": bracket_binding["endpoints"]["post"][
   671	            "content_digest"
   672	        ],
   673	        "bracket_binding_sha256": bracket_binding_sha256,
   674	        "terminal_ledger_head_sha256": bracket_binding["terminal_head"][
   675	            "head_digest"
   676	        ],
   677	        "observed_drift_s": "0.001000",
   678	        "allowance_rule": generalized.V2_ALLOWANCE_RULE,
   679	        "bracket_screen_s": generalized.V2_BRACKET_SCREEN_S,
   680	        "applied_allowance_s": generalized.V2_BRACKET_SCREEN_S,
   681	        "allowance_embedding_count": 1,
   682	        "extraction_report_sha256": extraction_report_sha256,
   683	        "absolute_floor_full_precision": absolute_full,
   684	        "comparative_floor_full_precision": comparative_full,
   685	        "operative_floor_full_precision": comparative_full,
   686	        "absolute_floor_six_decimal": "6.294380",
   687	        "comparative_floor_six_decimal": "13.998037",
   688	        "operative_floor_six_decimal": "13.998037",
   689	    }
   690	
   691	
   692	def _fixture_canonical_sha256(value: object) -> str:
   693	    payload = json.dumps(
   694	        value,
   695	        sort_keys=True,
   696	        separators=(",", ":"),
   697	        ensure_ascii=False,
   698	        allow_nan=False,
   699	    ).encode("utf-8")
   700	    return hashlib.sha256(payload).hexdigest()
   800	        plan_sha256=plan_sha256,
   801	        evidence_root_id=evidence_root_id,
   802	        runs_root=str(runs_root.resolve(strict=False)),
   803	        capability_receipt_digest=capability_receipt,
   804	        finalized_slots={"pre": observations[0], "post": observations[1]},
   805	    )
   806	    return binding, receipts, observations, session
   807	
   808	
   809	def synthetic_v2_fixture() -> tuple[
   810	    dict,
   811	    dict[str, generalized.V2ProducerInputs],
   812	    SimpleNamespace,
   813	]:
   814	    base_plan, base_absolute, base_comparative = seven_b_components()
   815	    producers = []
   816	    inputs = {}
   817	    all_cell_ids = []
   818	    all_group_ids = []
   819	    all_allowlists = []
   820	    ledger_receipts: list[dict] = []
   821	    ledger_observations: list[SimpleNamespace] = []
   822	    ledger_sessions: dict[str, SimpleNamespace] = {}
   823	    for producer_index in range(2):
   824	        plan_id = f"synthetic-d117-floor-plan-{producer_index}"
   825	        plan_sha256 = f"{producer_index + 2:x}" * 64
   826	        declared_sha256 = plan_sha256
   827	        sidecar_sha256 = f"{producer_index + 6:x}" * 64
   828	        evidence_root_id = f"synthetic-d117-root-{producer_index}"
   829	        evidence_root = Path(f"/synthetic/evidence/{evidence_root_id}")
   830	        plan = {
   831	            **base_plan,
   832	            "plan_id": plan_id,
   833	            "calibration_scope": "production_window",
   834	        }
   835	        binding, receipts, observations, session = _synthetic_bracket_evidence(
   836	            producer_index,
   837	            plan_id=plan_id,
   838	            plan_sha256=plan_sha256,
   839	            evidence_root_id=evidence_root_id,
   840	            runs_root=evidence_root,
   841	            sequence_start=1 + 3 * producer_index,
   842	        )
   843	        ledger_receipts.extend(receipts)
   844	        ledger_observations.extend(observations)
   845	        ledger_sessions[session.session_id] = session
   846	        bracket_binding_sha256 = _fixture_artifact_sha256(binding)
   847	        extraction_spec_sha256 = f"{producer_index + 2:x}" * 64
   848	        role_rows = []
   849	        report_rows = []
   850	        for role in ("decode", "prefill"):
   851	            family_id = f"synthetic-{producer_index}-{role}"
   852	            absolute, comparative, family_binding = _role_components(
   853	                replace(base_absolute, evidence_root_id=evidence_root_id),
   854	                replace(base_comparative, evidence_root_id=evidence_root_id),
   855	                role=role,
   856	                family_id=family_id,
   857	                plan_id=plan_id,
   858	                plan_sha256=plan_sha256,
   859	            )
   860	            absolute = replace(absolute, spec_sha256=extraction_spec_sha256)
   861	            comparative = replace(
   862	                comparative, spec_sha256=extraction_spec_sha256
   863	            )
   864	            cell_id = f"cell-{producer_index}-{role}"
   865	            group_id = f"transport-{producer_index}-{role}"
   866	            allowlist = [
   867	                {
   868	                    "condition_family_id": family_id,
   869	                    "condition_family_sha256": family_binding[
   870	                        "condition_family_sha256"
   871	                    ],
   872	                }
   873	            ]
   874	            report_rows.append(
   875	                {
   876	                    "cell_id": cell_id,
   877	                    "observed_drift_s": "0.001000",
   878	                    "applied_allowance_s": generalized.V2_BRACKET_SCREEN_S,
   879	                    "absolute_floor_full_precision": "6.294380135190098",
   880	                    "comparative_floor_full_precision": "13.998036715259254",
   881	                    "operative_floor_full_precision": "13.998036715259254",
   882	                    "absolute_floor_six_decimal": "6.294380",
   883	                    "comparative_floor_six_decimal": "13.998037",
   884	                    "operative_floor_six_decimal": "13.998037",
   885	                }
   886	            )
   887	            role_rows.append(
   888	                (role, cell_id, group_id, allowlist, family_binding, absolute, comparative)
   889	            )
   890	        report = {
   891	            "diagnostics": {"published_claim_floor": False},
   892	            "floor_mint_postcollection": {
   893	                "schema_version": generalized.V2_EXTRACTION_POSTCOLLECTION_SCHEMA,
   894	                "cells": report_rows,
   895	            },
   896	        }
   897	        report_sha256 = _fixture_artifact_sha256(report)
   898	        role_inputs = {}
   899	        cell_pins = []
   900	        for (
   901	            role,
   902	            cell_id,
   903	            group_id,
   904	            allowlist,
   905	            family_binding,
   906	            absolute,
   907	            comparative,
   908	        ) in role_rows:
   909	            absolute = replace(
   910	                absolute, report=report, report_sha256=report_sha256
   911	            )
   912	            comparative = replace(
   913	                comparative, report=report, report_sha256=report_sha256
   914	            )
   915	            cell_pins.append(
   916	                {
   917	                    "role": role,
   918	                    "cell_id": cell_id,
   919	                    "transport_group_id": group_id,
   920	                    "condition_family_id": family_binding[
   921	                        "condition_family_id"
   922	                    ],
   923	                    "condition_family_sha256": family_binding[
   924	                        "condition_family_sha256"
   925	                    ],
   926	                    "metric": f"phase_energy_j.{role}",
   927	                    "window_class": "phase",
   928	                    "target_precheck_path": ["phase", role],
   929	                    "allowed_consumer_condition_families": allowlist,
   930	                    "absolute": _v2_component_pin(absolute),
   931	                    "comparative": _v2_component_pin(comparative),
   932	                    "postcollection": _v2_postcollection(
   933	                        absolute,
   934	                        comparative,
   935	                        bracket_binding=binding,
   936	                        bracket_binding_sha256=bracket_binding_sha256,
   937	                        extraction_report_sha256=report_sha256,
   938	                    ),
   939	                }
   940	            )
   941	            role_inputs[role] = generalized.V2CellComponents(
   942	                absolute=absolute,
   943	                comparative=comparative,
   944	                allowed_consumer_condition_families=(family_binding,),
   945	            )
   946	            all_cell_ids.append(cell_id)
   947	            all_group_ids.append(group_id)
   948	            all_allowlists.append(
   949	                {
   950	                    "transport_group_id": group_id,
   951	                    "cell_ids": [cell_id],
   952	                    "allowed_consumer_condition_families": allowlist,
   953	                }
   954	            )
   955	        components = [
   956	            component
   957	            for role_input in role_inputs.values()
   958	            for component in (role_input.absolute, role_input.comparative)
   959	        ]
   960	        unique_members = {
   961	            member.bundle_id
   962	            for component in components
   963	            for member in component.members
   964	        }
   965	        runtime_identity_sha256 = components[0].source_regime[
   966	            "stack_identity_sha256"
   967	        ]
   968	        acceptance = {
   969	            "schema_version": "joulewise.calibration_acceptance_bound.v2",
   970	            "acceptance_id": "d079-calibration-acceptance-v2",
   971	            "derivation_sha256": "b" * 64,
   972	        }
   973	        producer = {
   974	            "plan": {
   975	                "plan_id": plan_id,
   976	                "sha256": plan_sha256,
   977	                "declared_sha256": declared_sha256,
   978	                "sidecar_sha256": sidecar_sha256,
   979	                "relative_path": f"plans/{plan_id}.json",
   980	                "declared_calibration_scope": "production_window",
   981	                "artifact_calibration_scope": "production_window",
   982	            },
   983	            "evidence_root_id": evidence_root_id,
   984	            "component_artifact": {
   985	                "artifact_id": f"component-artifact-{producer_index}",
   986	                "sha256": "0" * 64,
   987	            },
   988	            "model_runtime_config": {
   989	                "model_artifact_sha256": components[0].source_regime[
   990	                    "stack_identity"
   991	                ]["model_artifact_sha256"],
   992	                "runtime_identity_sha256": runtime_identity_sha256,
   993	                "config_set_sha256": components[
   994	                    0
   995	                ].scientific_config_identity_sha256,
   996	            },
   997	            "extraction_spec": {
   998	                "sha256": extraction_spec_sha256,
   999	                "member_count": len(unique_members),
  1000	            },
  1001	            "calibration_acceptance": {
  1002	                "acceptance_id": acceptance["acceptance_id"],
  1003	                "artifact_sha256": "a" * 64,
  1004	                "derivation_sha256": acceptance["derivation_sha256"],
  1005	                "derivation_rule_id": acceptance["schema_version"],
  1006	            },
  1007	            "cells": cell_pins,
  1008	        }
  1009	        producers.append(producer)
  1010	        inputs[plan_id] = generalized.V2ProducerInputs(
  1011	            plan=plan,
  1012	            cells=role_inputs,
  1013	            evidence_root=evidence_root,
  1014	            plan_sha256=plan_sha256,
  1015	            plan_declared_sha256=declared_sha256,
  1016	            plan_sidecar_sha256=sidecar_sha256,
  1017	            calibration_acceptance=acceptance,
  1018	            calibration_acceptance_sha256="a" * 64,
  1019	            bracket_binding=binding,
  1020	            bracket_binding_sha256=bracket_binding_sha256,
  1021	        )
  1022	    pinset = {
  1023	        "schema_version": generalized.PINSET_SCHEMA_VERSION_V2,
  1024	        "mint_tool_version": generalized.V2_MINT_TOOL_VERSION,
  1025	        "producer_plans": producers,
  1026	        "aggregate": {
  1027	            "artifact_id": "synthetic-d117-four-cell-floor",
  1028	            "plan_set_id": "synthetic-d117-plan-set",
  1029	            "producer_set_sha256": "0" * 64,
  1030	            "calibration_scope": "production_window",
  1031	            "source_class": "prospective",
  1032	            "cell_composition_rule": generalized.V2_CELL_COMPOSITION_RULE,
  1033	            "consumer_floor_rule": generalized.V2_CONSUMER_FLOOR_RULE,
  1034	            "component_artifacts": [
  1035	                {
  1036	                    "plan_id": producer["plan"]["plan_id"],
  1037	                    "artifact_id": producer["component_artifact"][
  1038	                        "artifact_id"
  1039	                    ],
  1040	                    "sha256": "0" * 64,
  1041	                    "producer_pin_sha256": "0" * 64,
  1042	                }
  1043	                for producer in producers
  1044	            ],
  1045	            "cell_ids": all_cell_ids,
  1046	            "transport_allowlists": all_allowlists,
  1047	        },
  1048	    }
  1049	    ledger_snapshot = SimpleNamespace(
  1050	        valid=True,
  1051	        ledger_schema="joulewise.calibration_observation_ledger.v1",
  1052	        receipts=tuple(ledger_receipts),
  1053	        observations=tuple(ledger_observations),
  1054	        bracket_session_by_id=ledger_sessions,
  1055	        head_sequence=len(ledger_receipts),
  1056	        head_digest=ledger_receipts[-1]["receipt_digest"],
  1057	    )
  1058	    return pinset, inputs, ledger_snapshot
  1059	
  1060	
  1061	# Independent golden constants. They are regenerated only by an explicit
  1062	# fixture-review step, never by the mint implementation under test.
  1063	SYNTHETIC_COMPONENT_SHA256S = (
  1064	    "b0404c15df0b2e0afb445ab6cea9b2c08a7922e3d49fd7354b8aec05262d9851",
  1065	    "0543bb0d1282f84e78e6b7c03cc6eaf3903d470bcb58bf39cb9d63fda5922fef",
  1066	)
  1067	SYNTHETIC_PRODUCER_PIN_SHA256S = (
  1068	    "70e3c43269a2bdd4bfc651d136086b6b0b863c8a4f9de1a1716d81d879c44a8b",
  1069	    "e1f600ebbae32be565abdb64098d5c4046f101f041ea5bd8f7c2800b7f6a4278",
  1070	)
  1071	SYNTHETIC_PRODUCER_SET_SHA256 = (
  1072	    "f58ed63311a5e62a1b61dc9c43c653c0caddc5aa201ae17533a28eabaa397c11"
  1073	)
  1074	
  1075	
  1076	def _repair_v2_pinset_self_hashes(pinset: dict) -> None:
  1077	    """Repair only pinset self-hashes with an independent JSON oracle."""
  1078	
  1079	    for producer, entry in zip(
  1080	        pinset["producer_plans"],
  1081	        pinset["aggregate"]["component_artifacts"],
  1082	    ):
  1083	        entry["producer_pin_sha256"] = _fixture_canonical_sha256(producer)
  1084	    pinset["aggregate"]["producer_set_sha256"] = _fixture_canonical_sha256(
  1085	        pinset["producer_plans"]
  1086	    )
  1087	
  1088	
  1089	def freeze_synthetic_v2_pinset(
  1090	    root: Path,
  1091	) -> tuple[
  1092	    Path,
  1093	    str,
  1094	    dict[str, generalized.V2ProducerInputs],
  1095	    SimpleNamespace,
  1096	]:
  1097	    pinset, inputs, ledger_snapshot = synthetic_v2_fixture()
  1098	    for producer, entry, component_sha256, producer_sha256 in zip(
  1099	        pinset["producer_plans"],
  1100	        pinset["aggregate"]["component_artifacts"],
  1101	        SYNTHETIC_COMPONENT_SHA256S,
  1102	        SYNTHETIC_PRODUCER_PIN_SHA256S,
  1103	    ):
  1104	        producer["component_artifact"]["sha256"] = component_sha256
  1105	        entry["sha256"] = component_sha256
  1106	        entry["producer_pin_sha256"] = producer_sha256
  1107	    pinset["aggregate"]["producer_set_sha256"] = (
  1108	        SYNTHETIC_PRODUCER_SET_SHA256
  1109	    )
  1110	    path, digest = write_pinset(root, pinset)
  1111	    return path, digest, inputs, ledger_snapshot
  1112	
  1113	
  1114	class PinsetTests(unittest.TestCase):
  1115	    def test_mint1_pinset_is_exactly_the_original_hard_pin_set(self) -> None:
   700	        producer_custody_pins: list[tuple[object, ...]] = []
   701	        for cell_index, cell_value in enumerate(cells):
   702	            cell_label = f"{label}.cells[{cell_index}]"
   703	            cell = _object(
   704	                cell_value,
   705	                cell_label,
   706	                {
   707	                    "role",
   708	                    "cell_id",
   709	                    "transport_group_id",
   710	                    "condition_family_id",
   711	                    "condition_family_sha256",
   712	                    "metric",
   713	                    "window_class",
   714	                    "target_precheck_path",
   715	                    "allowed_consumer_condition_families",
   716	                    "absolute",
   717	                    "comparative",
   718	                    "postcollection",
   719	                },
   720	            )
   721	            role = _string(cell["role"], f"{cell_label}.role")
   722	            roles.append(role)
   723	            expected_metric = {
   724	                "decode": "phase_energy_j.decode",
   725	                "prefill": "phase_energy_j.prefill",
   726	            }.get(role)
   727	            if expected_metric is None:
   728	                raise MintError(f"{cell_label}.role must be decode or prefill")
   729	            if cell["metric"] != expected_metric:
   730	                raise MintError(
   731	                    f"{cell_label}.metric must equal {expected_metric!r}"
   732	                )
   733	            if cell["window_class"] != "phase":
   734	                raise MintError(f"{cell_label}.window_class must equal 'phase'")
   735	            if cell["target_precheck_path"] != ["phase", role]:
   736	                raise MintError(
   737	                    f"{cell_label}.target_precheck_path must equal ['phase', {role!r}]"
   738	                )
   739	            cell_id = _string(cell["cell_id"], f"{cell_label}.cell_id")
   740	            group_id = _string(
   741	                cell["transport_group_id"],
   742	                f"{cell_label}.transport_group_id",
   743	            )
   744	            cell_ids.append(cell_id)
   745	            group_ids.append(group_id)
   746	            cell_values.append(cell)
   747	            _string(
   748	                cell["condition_family_id"],
   749	                f"{cell_label}.condition_family_id",
   750	            )
   751	            _sha256(
   752	                cell["condition_family_sha256"],
   753	                f"{cell_label}.condition_family_sha256",
   754	            )
   755	            _consumer_family_pins(
   756	                cell["allowed_consumer_condition_families"],
   757	                f"{cell_label}.allowed_consumer_condition_families",
   758	            )
   759	            absolute = _parse_v2_component(cell["absolute"], f"{cell_label}.absolute")
   760	            comparative = _parse_v2_component(
   761	                cell["comparative"], f"{cell_label}.comparative"
   762	            )
   763	            if absolute.evidence_root_id != evidence_root_id or (
   764	                comparative.evidence_root_id != evidence_root_id
   765	            ):
   766	                raise MintError(
   767	                    f"{cell_label}: component evidence_root_id must equal the producer root"
   768	                )
   769	            for component_name in ("absolute", "comparative"):
   770	                component = cell[component_name]
   771	                if (
   772	                    component["extraction_spec_sha256"] != extraction["sha256"]
   773	                    or component["extraction_spec_members"]
   774	                    != extraction["member_count"]
   775	                ):
   776	                    raise MintError(
   777	                        f"{cell_label}.{component_name}: extraction-spec inventory "
   778	                        "must equal the producer pins"
   779	                    )
   780	            _parse_v2_postcollection(
   781	                cell["postcollection"], f"{cell_label}.postcollection"
   782	            )
   783	            post = cell["postcollection"]
   784	            producer_custody_pins.append(
   785	                tuple(
   786	                    post[name]
   787	                    for name in (
   788	                        "pre_receipt_sha256",
   789	                        "pre_content_sha256",
   790	                        "post_receipt_sha256",
   791	                        "post_content_sha256",
   792	                        "bracket_binding_sha256",
   793	                        "terminal_ledger_head_sha256",
   794	                        "observed_drift_s",
   795	                        "applied_allowance_s",
   796	                        "extraction_report_sha256",
   797	                    )
   798	                )
   799	            )
   800	            if (
   801	                post["absolute_evaluation_basis_sha256"]
   802	                != absolute.evaluation_basis_sha256
   803	                or post["absolute_evaluation_basis_members"]
   804	                != absolute.evaluation_basis_members
   805	                or post["comparative_evaluation_basis_sha256"]
   806	                != comparative.evaluation_basis_sha256
   807	                or post["comparative_evaluation_basis_members"]
   808	                != comparative.evaluation_basis_members
   809	            ):
   810	                raise MintError(
   811	                    f"{cell_label}.postcollection evaluation basis disagrees with component pins"
   812	                )
   813	            component_member_universe.update(
   814	                bundle_id for bundle_id, _digest in _member_pins(
   815	                    cell["absolute"]["members"], f"{cell_label}.absolute.members"
   816	                )
   817	            )
   818	            component_member_universe.update(
   819	                bundle_id for bundle_id, _digest in _member_pins(
   820	                    cell["comparative"]["members"],
   821	                    f"{cell_label}.comparative.members",
   822	                )
   823	            )
   824	        if set(roles) != {"decode", "prefill"} or len(roles) != len(set(roles)):
   825	            raise MintError(f"{label}.cells must contain one decode and one prefill role")
   826	        if len(set(producer_custody_pins)) != 1:
   827	            raise MintError(
   828	                f"{label}.cells must share one authenticated producer custody record"
   829	            )
   830	        if len(component_member_universe) != extraction["member_count"]:
   831	            raise MintError(
   832	                f"{label}.extraction_spec.member_count must equal the unique pinned member count"
   833	            )
   834	
   835	    if len(plan_ids) != len(set(plan_ids)):
   836	        raise MintError("pinset producer plan ids must be unique")
   837	    if len(cell_ids) != 4 or len(cell_ids) != len(set(cell_ids)):
   838	        raise MintError("pinset must define exactly four unique cell ids")
   839	    if len(group_ids) != 4 or len(group_ids) != len(set(group_ids)):
   840	        raise MintError("pinset must define exactly four unique transport groups")
   841	
   842	    aggregate = _object(
   843	        root["aggregate"],
   844	        "pinset.aggregate",
   845	        {
   846	            "artifact_id",
   847	            "plan_set_id",
   848	            "producer_set_sha256",
   849	            "calibration_scope",
   850	            "source_class",
   851	            "cell_composition_rule",
   852	            "consumer_floor_rule",
   853	            "component_artifacts",
   854	            "cell_ids",
   855	            "transport_allowlists",
   856	        },
   857	    )
   858	    _string(aggregate["artifact_id"], "pinset.aggregate.artifact_id")
   859	    _string(aggregate["plan_set_id"], "pinset.aggregate.plan_set_id")
   860	    _sha256(
   861	        aggregate["producer_set_sha256"],
   862	        "pinset.aggregate.producer_set_sha256",
   863	    )
   864	    if aggregate["calibration_scope"] != "production_window":
   865	        raise MintError("pinset.aggregate.calibration_scope must equal 'production_window'")
   866	    if aggregate["source_class"] != "prospective":
   867	        raise MintError("pinset.aggregate.source_class must equal 'prospective'")
   868	    if aggregate["cell_composition_rule"] != V2_CELL_COMPOSITION_RULE:
   869	        raise MintError(
   870	            f"pinset.aggregate.cell_composition_rule must equal {V2_CELL_COMPOSITION_RULE!r}"
  2380	        plan_pins = producer["plan"]
  2381	        plan_id = plan_pins["plan_id"]
  2382	        inputs = producer_inputs.get(plan_id)
  2383	        if inputs is None:
  2384	            raise MintError(f"missing authenticated producer inputs for {plan_id!r}")
  2385	        if set(inputs.cells) != {"decode", "prefill"}:
  2386	            raise MintError(
  2387	                f"producer inputs for {plan_id!r} must contain decode and prefill"
  2388	            )
  2389	        if inputs.plan.get("plan_id") != plan_id:
  2390	            raise MintError(f"producer {plan_id!r}: calibration plan identity mismatch")
  2391	        _v2_gate_producer_inventory(producer, inputs)
  2392	        producer_cells: list[Mapping[str, Any]] = []
  2393	        producer_groups: list[Mapping[str, Any]] = []
  2394	        for cell_index, cell_pins in enumerate(producer["cells"]):
  2395	            role = cell_pins["role"]
  2396	            cell_inputs = inputs.cells[role]
  2397	            _v2_gate_component(
  2398	                cell_inputs.absolute,
  2399	                cell_pins["absolute"],
  2400	                label=f"producer[{producer_index}].{role}.absolute",
  2401	                metric=cell_pins["metric"],
  2402	                window_class=cell_pins["window_class"],
  2403	            )
  2404	            _v2_gate_component(
  2405	                cell_inputs.comparative,
  2406	                cell_pins["comparative"],
  2407	                label=f"producer[{producer_index}].{role}.comparative",
  2408	                metric=cell_pins["metric"],
  2409	                window_class=cell_pins["window_class"],
  2410	            )
  2411	            _v2_gate_postcollection(
  2412	                producer=producer,
  2413	                cell_pins=cell_pins,
  2414	                cell_inputs=cell_inputs,
  2415	                producer_inputs=inputs,
  2416	                ledger_snapshot=calibration_ledger_snapshot,
  2417	            )
  2418	            configured_pins = _v2_mint_pinset(producer, cell_pins)
  2419	            core = _configured_core(
  2420	                configured_pins,
  2421	                pinset_path=pinset_path,
  2422	                expected_pinset_sha256=pinset_sha256,
  2423	            )
  2424	            try:
  2425	                cell_artifact = _mint_v2_cell_artifact(
  2426	                    core=core,
  2427	                    producer=producer,
  2428	                    cell_pins=cell_pins,
  2429	                    plan=inputs.plan,
  2430	                    absolute=cell_inputs.absolute,
  2431	                    comparative=cell_inputs.comparative,
  2432	                    project_commit=project_commit,
  2433	                    project_tree_state=project_tree_state,
  2434	                )
  2435	            except core.MintError as exc:
  2436	                raise MintError(str(exc)) from exc
  2437	            cell = copy.deepcopy(cell_artifact["cells"][0])
  2438	            group = copy.deepcopy(cell_artifact["transport_groups"][0])
  2439	            allowed = _v2_allowed_families(
  2440	                cell_inputs.allowed_consumer_condition_families,
  2441	                cell_pins["allowed_consumer_condition_families"],
  2442	                label=f"producer[{producer_index}].cells[{cell_index}].allowlist",
  2443	            )
  2444	            group["allowed_consumer_condition_families"] = allowed
  2445	            producer_cells.append(cell)
  2446	            producer_groups.append(group)
  2447	
  2448	        first_cell_artifact = cell_artifact
  2449	        component = {
  2450	            **copy.deepcopy(first_cell_artifact),
  2451	            "artifact_id": producer["component_artifact"]["artifact_id"],
  2452	            "cells": producer_cells,
  2453	            "transport_groups": producer_groups,
  2454	        }
  2455	        component_errors = validate_floor_artifact(
  2456	            artifact=component,
  2457	            pinset_path=pinset_path,
  2458	            pinset_sha256=pinset_sha256,
  2459	            _skip_v2_hash_binding=True,
  2460	        )
  2461	        if component_errors:
  2462	            raise MintError(
  2463	                f"constructed v2 component artifact is invalid: {component_errors[0]}"
  2464	            )
  2465	        component_artifacts.append(component)
  2466	        all_cells.extend(copy.deepcopy(producer_cells))
  2467	        all_groups.extend(copy.deepcopy(producer_groups))
  2468	        producer_plan_records.append(
  2469	            {
  2470	                "plan_id": plan_id,
  2471	                "declared_calibration_scope": plan_pins[
  2472	                    "declared_calibration_scope"
  2473	                ],
  2474	                "relative_path": plan_pins["relative_path"],
  2475	                "sha256": plan_pins["sha256"],
  2476	            }
  2477	        )
  2478	
  2479	    aggregate = pinset.value["aggregate"]
  2480	    implementation = copy.deepcopy(
  2481	        component_artifacts[0]["provenance"]["implementation"]
  2482	    )
  2483	    artifact = {
  2484	        **copy.deepcopy(component_artifacts[0]),
  2485	        "artifact_id": aggregate["artifact_id"],
  2486	        "calibration_scope": aggregate["calibration_scope"],
  2487	        "source_class": aggregate["source_class"],
  2488	        "provenance": {
  2489	            "calibration_plan": {
  2490	                "plan_id": aggregate["plan_set_id"],
  2491	                "declared_calibration_scope": "production_window",
  2492	                "relative_path": Path(pinset_path).name,
  2493	                "sha256": aggregate["producer_set_sha256"],
  2494	            },
  2495	            "producer_calibration_plans": producer_plan_records,
  2496	            "mint_tool_version": V2_MINT_TOOL_VERSION,
  2497	            "implementation": implementation,
  2498	        },
  2499	        "cells": all_cells,
  2500	        "transport_groups": all_groups,
  2501	    }
  2502	    errors = validate_floor_artifact(
  2503	        artifact=artifact,
  2504	        pinset_path=pinset_path,
  2505	        pinset_sha256=pinset_sha256,

exec
/bin/zsh -lc 'set -o pipefail; PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/joulewise-u3-reaudit-pycache python3 -m unittest -v tests.test_detection_floor tests.test_analysis_claims tests.test_analysis_integration 2>&1 | tail -n 8' in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u3
exec
/bin/zsh -lc 'set -o pipefail; PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/joulewise-u3-reaudit-pycache python3 -m unittest -v tests.test_mint_floor_artifact 2>&1 | tail -n 8' in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u3
exec
/bin/zsh -lc 'set -o pipefail; PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/joulewise-u3-reaudit-pycache python3 -m unittest -v tests.test_mint_floor_artifact_generalized 2>&1 | tail -n 8' in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u3
 succeeded in 1006ms:
test_required_stack_fields_remain_fail_closed (tests.test_mint_floor_artifact.StackIdentityParityTests.test_required_stack_fields_remain_fail_closed) ... ok
test_sampler_is_required_on_both_mint_and_claim_sides (tests.test_mint_floor_artifact.StackIdentityParityTests.test_sampler_is_required_on_both_mint_and_claim_sides) ... ok
test_windows_tokenizer_path_normalizes_like_mint (tests.test_mint_floor_artifact.StackIdentityParityTests.test_windows_tokenizer_path_normalizes_like_mint) ... ok

----------------------------------------------------------------------
Ran 34 tests in 0.620s

OK

 succeeded in 2677ms:
test_v2_decimal_pins_require_plain_unsigned_strings (tests.test_mint_floor_artifact_generalized.V2PinsetAndMintTests.test_v2_decimal_pins_require_plain_unsigned_strings) ... ok
test_v2_input_manifest_routes_all_authenticated_evidence_files (tests.test_mint_floor_artifact_generalized.V2PinsetAndMintTests.test_v2_input_manifest_routes_all_authenticated_evidence_files) ... ok
test_v2_mint_does_not_render_or_round_floor_literals (tests.test_mint_floor_artifact_generalized.V2PinsetAndMintTests.test_v2_mint_does_not_render_or_round_floor_literals) ... ok

----------------------------------------------------------------------
Ran 39 tests in 2.271s

OK

 succeeded in 26309ms:
test_v4_valid_exact_plus_corrupted_same_bundle_clone_refuses (tests.test_analysis_integration.SupersessionAwareCooldownJoinTests.test_v4_valid_exact_plus_corrupted_same_bundle_clone_refuses) ... ok
test_valid_supersession_resolves_selected_occurrence (tests.test_analysis_integration.SupersessionAwareCooldownJoinTests.test_valid_supersession_resolves_selected_occurrence) ... ok
test_validated_log_supersession_selects_governing_cooldown_row (tests.test_analysis_integration.SupersessionAwareCooldownJoinTests.test_validated_log_supersession_selects_governing_cooldown_row) ... ok

----------------------------------------------------------------------
Ran 249 tests in 25.737s

OK

exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/joulewise-u3-reaudit-pycache python3 - <<'PY'
import copy, tempfile
from pathlib import Path
from scripts import mint_floor_artifact_generalized as g
from tests.test_mint_floor_artifact_generalized import (
    freeze_synthetic_v2_pinset, load_json, write_pinset,
    _repair_v2_pinset_self_hashes,
)

fields = {
    'pre_receipt_sha256': '0' * 64,
    'pre_content_sha256': '1' * 64,
    'post_receipt_sha256': '2' * 64,
    'post_content_sha256': '3' * 64,
    'bracket_binding_sha256': '4' * 64,
    'terminal_ledger_head_sha256': '5' * 64,
    'extraction_report_sha256': '6' * 64,
    'observed_drift_s': '0.012000',
    'applied_allowance_s': '0.0108180',
}

def attempt(candidate, root, inputs, snapshot, label):
    _repair_v2_pinset_self_hashes(candidate)
    path, digest = write_pinset(root, candidate)
    try:
        g.mint_multi_cell_authenticated_artifact(
            pinset_path=path,
            pinset_sha256=digest,
            producer_inputs=inputs,
            calibration_ledger_snapshot=snapshot,
            project_commit='0' * 40,
            project_tree_state='clean',
        )
    except g.MintError as exc:
        print(f'{label}: REFUSED: {exc}')
    else:
        print(f'{label}: MINTED')

with tempfile.TemporaryDirectory(dir='/tmp') as tmp:
    root = Path(tmp)
    path, _digest, inputs, snapshot = freeze_synthetic_v2_pinset(root)
    source = load_json(path)
    combined = copy.deepcopy(source)
    for cell in combined['producer_plans'][0]['cells']:
        for field, replacement in fields.items():
            if field == 'applied_allowance_s':
                replacement = '0.012000'
            cell['postcollection'][field] = replacement
    attempt(combined, root, inputs, snapshot, 'combined_all_custody_fields')

    for field, replacement in fields.items():
        candidate = copy.deepcopy(source)
        for cell in candidate['producer_plans'][0]['cells']:
            cell['postcollection'][field] = replacement
            if field == 'observed_drift_s':
                cell['postcollection']['applied_allowance_s'] = '0.012000'
        attempt(candidate, root, inputs, snapshot, field)
PY" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u3
 succeeded in 394ms:
combined_all_custody_fields: REFUSED: postcollection_evidence_mismatch: bracket_binding_sha256 mismatch against supplied bracket-binding artifact bytes
pre_receipt_sha256: REFUSED: postcollection_evidence_mismatch: pre_receipt_sha256 mismatch against authenticated ledger pre observation
pre_content_sha256: REFUSED: postcollection_evidence_mismatch: pre_content_sha256 mismatch against authenticated ledger pre observation
post_receipt_sha256: REFUSED: postcollection_evidence_mismatch: post_receipt_sha256 mismatch against authenticated ledger post observation
post_content_sha256: REFUSED: postcollection_evidence_mismatch: post_content_sha256 mismatch against authenticated ledger post observation
bracket_binding_sha256: REFUSED: postcollection_evidence_mismatch: bracket_binding_sha256 mismatch against supplied bracket-binding artifact bytes
terminal_ledger_head_sha256: REFUSED: postcollection_evidence_mismatch: terminal_ledger_head_sha256 mismatch against authenticated bracket-binding terminal head
extraction_report_sha256: REFUSED: postcollection_evidence_mismatch: extraction_report_sha256 mismatch against supplied absolute extraction-report artifact bytes
observed_drift_s: REFUSED: postcollection_evidence_mismatch: observed_drift_s mismatch against authenticated ledger endpoint bounds
applied_allowance_s: REFUSED: postcollection_evidence_mismatch: applied_allowance_s mismatch against authenticated extraction-report record

exec
/bin/zsh -lc "rg -n 'mint_multi_cell_authenticated_artifact\\(|mint_multi_cell_floor_artifact\\(|_authenticate_v2_inputs\\(' --glob '*.py' --glob '"'!tests/**'"'; rg -n 'mint_floor_artifact_generalized.py|--v2-input-manifest' pyproject.toml scripts docs -g '*.py' -g '*.md' -g '*.toml' | head -160; rg -n 'load_calibration_ledger_snapshot|head_uncommitted|require_committed_pin|calibration acceptance' tests/test_calibration_ledger.py tests/test_calibration_bracketing.py tests/test_mint_floor_artifact.py | head -220" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u3
 succeeded in 0ms:
scripts/mint_floor_artifact_generalized.py:2768:def mint_multi_cell_authenticated_artifact(
scripts/mint_floor_artifact_generalized.py:2890:def _authenticate_v2_inputs(
scripts/mint_floor_artifact_generalized.py:3190:def mint_multi_cell_floor_artifact(
scripts/mint_floor_artifact_generalized.py:3208:    inputs, evidence_roots, ledger_snapshot = _authenticate_v2_inputs(
scripts/mint_floor_artifact_generalized.py:3328:            mint_multi_cell_floor_artifact(
scripts/mint_floor_artifact_generalized.py:3291:    parser.add_argument("--v2-input-manifest", type=Path)
scripts/mint_floor_artifact_generalized.py:3327:                raise MintError("final v2 pinset requires --v2-input-manifest")
docs/strategy/2026-08-07-paper-portfolio/reviews/rev-energy-nutrition-label.md:113:Compounding this: "no hand-copied scientific numbers and byte-linked provenance" implies the renderer hooks the governed mint chain — `scripts/mint_floor_artifact_generalized.py` / `joulewise/detection_floor.py`, i.e. **U3, on the D-117 critical path**. The proposal never specifies whether the label layer is upstream (critical-path-perturbing) or a downstream read-only consumer of minted artifacts. That ambiguity is the difference between "free" and "delays the three windows."
docs/strategy/2026-08-07-paper-portfolio/reviews/rev-energy-nutrition-label.md:170:- If the label serialization touches `mint_floor_artifact_generalized.py` / `detection_floor.py` rather than consuming minted artifacts read-only, kill it until after the three D-117 windows land. Nothing goes on the critical path for a formatting layer.
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-prefill-scaling-laws.md:2165:The current mechanism is `scripts/floor_mint_pinsets/mint1.json` plus `scripts/mint_floor_artifact_generalized.py`. It already embodies the right principle—plans supply hard pins and the mint compares rather than derives—but it remains structurally limited:
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-prefill-scaling-laws.md:2488:| U3 — pinset v2 and multi-cell mint | `scripts/mint_floor_artifact_generalized.py`; `scripts/floor_mint_pinsets/schema_v2.json`; `joulewise/detection_floor.py`; `tests/test_mint_floor_artifact_generalized.py` | Decode and prefill metrics, per-plan component pins, aggregate four-cell pins, no derived literals, no cross-stack sum, v1 compatibility. Focused parity/refusal tests plus full suite. | Independent of U1/U2 |
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-quantization-ladder.md:1530:The current mechanism is `scripts/floor_mint_pinsets/mint1.json` plus `scripts/mint_floor_artifact_generalized.py`. It already embodies the right principle—plans supply hard pins and the mint compares rather than derives—but it remains structurally limited:
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-quantization-ladder.md:1857:| U3 — pinset v2 and multi-cell mint | `scripts/mint_floor_artifact_generalized.py`; `scripts/floor_mint_pinsets/schema_v2.json`; `joulewise/detection_floor.py`; `tests/test_mint_floor_artifact_generalized.py` | Decode and prefill metrics, per-plan component pins, aggregate four-cell pins, no derived literals, no cross-stack sum, v1 compatibility. Focused parity/refusal tests plus full suite. | Independent of U1/U2 |
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-quantization-ladder.md:2914:The current mechanism is `scripts/floor_mint_pinsets/mint1.json` plus `scripts/mint_floor_artifact_generalized.py`. It already embodies the right principle—plans supply hard pins and the mint compares rather than derives—but it remains structurally limited:
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-quantization-ladder.md:3241:| U3 — pinset v2 and multi-cell mint | `scripts/mint_floor_artifact_generalized.py`; `scripts/floor_mint_pinsets/schema_v2.json`; `joulewise/detection_floor.py`; `tests/test_mint_floor_artifact_generalized.py` | Decode and prefill metrics, per-plan component pins, aggregate four-cell pins, no derived literals, no cross-stack sum, v1 compatibility. Focused parity/refusal tests plus full suite. | Independent of U1/U2 |
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-PRAGMATICS-FIRST.md:1088:The current mechanism is `scripts/floor_mint_pinsets/mint1.json` plus `scripts/mint_floor_artifact_generalized.py`. It already embodies the right principle—plans supply hard pins and the mint compares rather than derives—but it remains structurally limited:
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-PRAGMATICS-FIRST.md:1411:| U3 — pinset v2 and multi-cell mint | `scripts/mint_floor_artifact_generalized.py`; `scripts/floor_mint_pinsets/schema_v2.json`; `joulewise/detection_floor.py`; `tests/test_mint_floor_artifact_generalized.py` | Decode and prefill metrics, per-plan component pins, aggregate four-cell pins, no derived literals, no cross-stack sum, v1 compatibility. Focused parity/refusal tests plus full suite. | Independent of U1/U2 |
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-PRAGMATICS-FIRST.md:3048:Compounding this: "no hand-copied scientific numbers and byte-linked provenance" implies the renderer hooks the governed mint chain — `scripts/mint_floor_artifact_generalized.py` / `joulewise/detection_floor.py`, i.e. **U3, on the D-117 critical path**. The proposal never specifies whether the label layer is upstream (critical-path-perturbing) or a downstream read-only consumer of minted artifacts. That ambiguity is the difference between "free" and "delays the three windows."
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-PRAGMATICS-FIRST.md:3105:- If the label serialization touches `mint_floor_artifact_generalized.py` / `detection_floor.py` rather than consuming minted artifacts read-only, kill it until after the three D-117 windows land. Nothing goes on the critical path for a formatting layer.
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-PRAGMATICS-FIRST.md:8480:Compounding this: "no hand-copied scientific numbers and byte-linked provenance" implies the renderer hooks the governed mint chain — `scripts/mint_floor_artifact_generalized.py` / `joulewise/detection_floor.py`, i.e. **U3, on the D-117 critical path**. The proposal never specifies whether the label layer is upstream (critical-path-perturbing) or a downstream read-only consumer of minted artifacts. That ambiguity is the difference between "free" and "delays the three windows."
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-PRAGMATICS-FIRST.md:8537:- If the label serialization touches `mint_floor_artifact_generalized.py` / `detection_floor.py` rather than consuming minted artifacts read-only, kill it until after the three D-117 windows land. Nothing goes on the critical path for a formatting layer.
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:2253:The current mechanism is `scripts/floor_mint_pinsets/mint1.json` plus `scripts/mint_floor_artifact_generalized.py`. It already embodies the right principle—plans supply hard pins and the mint compares rather than derives—but it remains structurally limited:
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:2576:| U3 — pinset v2 and multi-cell mint | `scripts/mint_floor_artifact_generalized.py`; `scripts/floor_mint_pinsets/schema_v2.json`; `joulewise/detection_floor.py`; `tests/test_mint_floor_artifact_generalized.py` | Decode and prefill metrics, per-plan component pins, aggregate four-cell pins, no derived literals, no cross-stack sum, v1 compatibility. Focused parity/refusal tests plus full suite. | Independent of U1/U2 |
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:4456:Compounding this: "no hand-copied scientific numbers and byte-linked provenance" implies the renderer hooks the governed mint chain — `scripts/mint_floor_artifact_generalized.py` / `joulewise/detection_floor.py`, i.e. **U3, on the D-117 critical path**. The proposal never specifies whether the label layer is upstream (critical-path-perturbing) or a downstream read-only consumer of minted artifacts. That ambiguity is the difference between "free" and "delays the three windows."
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:4513:- If the label serialization touches `mint_floor_artifact_generalized.py` / `detection_floor.py` rather than consuming minted artifacts read-only, kill it until after the three D-117 windows land. Nothing goes on the critical path for a formatting layer.
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-cross-runtime-contrast.md:2122:The current mechanism is `scripts/floor_mint_pinsets/mint1.json` plus `scripts/mint_floor_artifact_generalized.py`. It already embodies the right principle—plans supply hard pins and the mint compares rather than derives—but it remains structurally limited:
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-cross-runtime-contrast.md:2449:| U3 — pinset v2 and multi-cell mint | `scripts/mint_floor_artifact_generalized.py`; `scripts/floor_mint_pinsets/schema_v2.json`; `joulewise/detection_floor.py`; `tests/test_mint_floor_artifact_generalized.py` | Decode and prefill metrics, per-plan component pins, aggregate four-cell pins, no derived literals, no cross-stack sum, v1 compatibility. Focused parity/refusal tests plus full suite. | Independent of U1/U2 |
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-cross-runtime-contrast.md:2619:The current mechanism is `scripts/floor_mint_pinsets/mint1.json` plus `scripts/mint_floor_artifact_generalized.py`. It already embodies the right principle—plans supply hard pins and the mint compares rather than derives—but it remains structurally limited:
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-refusal-as-result.md:1751:The current mechanism is `scripts/floor_mint_pinsets/mint1.json` plus `scripts/mint_floor_artifact_generalized.py`. It already embodies the right principle—plans supply hard pins and the mint compares rather than derives—but it remains structurally limited:
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-refusal-as-result.md:1908:| U3 — pinset v2 and multi-cell mint | `scripts/mint_floor_artifact_generalized.py`; `scripts/floor_mint_pinsets/schema_v2.json`; `joulewise/detection_floor.py`; `tests/test_mint_floor_artifact_generalized.py` | Decode and prefill metrics, per-plan component pins, aggregate four-cell pins, no derived literals, no cross-stack sum, v1 compatibility. Focused parity/refusal tests plus full suite. | Independent of U1/U2 |
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-param-scaling-energy.md:1543:The current mechanism is `scripts/floor_mint_pinsets/mint1.json` plus `scripts/mint_floor_artifact_generalized.py`. It already embodies the right principle—plans supply hard pins and the mint compares rather than derives—but it remains structurally limited:
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-param-scaling-energy.md:1872:| U3 — pinset v2 and multi-cell mint | `scripts/mint_floor_artifact_generalized.py`; `scripts/floor_mint_pinsets/schema_v2.json`; `joulewise/detection_floor.py`; `tests/test_mint_floor_artifact_generalized.py` | Decode and prefill metrics, per-plan component pins, aggregate four-cell pins, no derived literals, no cross-stack sum, v1 compatibility. Focused parity/refusal tests plus full suite. | Independent of U1/U2 |
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-drift-thermal-science.md:1655:The current mechanism is `scripts/floor_mint_pinsets/mint1.json` plus `scripts/mint_floor_artifact_generalized.py`. It already embodies the right principle—plans supply hard pins and the mint compares rather than derives—but it remains structurally limited:
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-drift-thermal-science.md:2271:| U3 — pinset v2 and multi-cell mint | `scripts/mint_floor_artifact_generalized.py`; `scripts/floor_mint_pinsets/schema_v2.json`; `joulewise/detection_floor.py`; `tests/test_mint_floor_artifact_generalized.py` | Decode and prefill metrics, per-plan component pins, aggregate four-cell pins, no derived literals, no cross-stack sum, v1 compatibility. Focused parity/refusal tests plus full suite. | Independent of U1/U2 |
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-drift-thermal-science.md:4772:scripts/mint_floor_artifact_generalized.py
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-drift-thermal-science.md:4780:tests/test_mint_floor_artifact_generalized.py
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-drift-thermal-science.md:5142:docs/process_traces/2026-08-04-calbracket-collision-consult/consult-solhigh.log:2074:./scripts/mint_floor_artifact_generalized.py:453:            "byte-frozen mint core interface drift: missing or renamed "
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-drift-thermal-science.md:5143:docs/process_traces/2026-08-04-calbracket-collision-consult/consult-solhigh.log:2075:./scripts/mint_floor_artifact_generalized.py:460:            "byte-frozen mint core interface drift: MintError is not a "
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-drift-thermal-science.md:5144:docs/process_traces/2026-08-04-calbracket-collision-consult/consult-solhigh.log:2077:./scripts/mint_floor_artifact_generalized.py:468:                "byte-frozen mint core interface drift: cannot inspect "
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-drift-thermal-science.md:5145:docs/process_traces/2026-08-04-calbracket-collision-consult/consult-solhigh.log:2078:./scripts/mint_floor_artifact_generalized.py:473:                "byte-frozen mint core interface drift: "
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-drift-thermal-science.md:5157:docs/process_traces/2026-08-04-calbracket-collision-consult/consult-solhigh.log:2170:./tests/test_mint_floor_artifact_generalized.py:1133:    def test_core_signature_drift_refuses_loudly(self) -> None:
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-tokenizer-honesty.md:1258:The current mechanism is `scripts/floor_mint_pinsets/mint1.json` plus `scripts/mint_floor_artifact_generalized.py`. It already embodies the right principle—plans supply hard pins and the mint compares rather than derives—but it remains structurally limited:
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-tokenizer-honesty.md:1589:| U3 — pinset v2 and multi-cell mint | `scripts/mint_floor_artifact_generalized.py`; `scripts/floor_mint_pinsets/schema_v2.json`; `joulewise/detection_floor.py`; `tests/test_mint_floor_artifact_generalized.py` | Decode and prefill metrics, per-plan component pins, aggregate four-cell pins, no derived literals, no cross-stack sum, v1 compatibility. Focused parity/refusal tests plus full suite. | Independent of U1/U2 |
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-open-explore-advisor.md:2148:The current mechanism is `scripts/floor_mint_pinsets/mint1.json` plus `scripts/mint_floor_artifact_generalized.py`. It already embodies the right principle—plans supply hard pins and the mint compares rather than derives—but it remains structurally limited:
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-open-explore-advisor.md:2475:| U3 — pinset v2 and multi-cell mint | `scripts/mint_floor_artifact_generalized.py`; `scripts/floor_mint_pinsets/schema_v2.json`; `joulewise/detection_floor.py`; `tests/test_mint_floor_artifact_generalized.py` | Decode and prefill metrics, per-plan component pins, aggregate four-cell pins, no derived literals, no cross-stack sum, v1 compatibility. Focused parity/refusal tests plus full suite. | Independent of U1/U2 |
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-mtp-energy.md:1242:The current mechanism is `scripts/floor_mint_pinsets/mint1.json` plus `scripts/mint_floor_artifact_generalized.py`. It already embodies the right principle—plans supply hard pins and the mint compares rather than derives—but it remains structurally limited:
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-mtp-energy.md:1565:| U3 — pinset v2 and multi-cell mint | `scripts/mint_floor_artifact_generalized.py`; `scripts/floor_mint_pinsets/schema_v2.json`; `joulewise/detection_floor.py`; `tests/test_mint_floor_artifact_generalized.py` | Decode and prefill metrics, per-plan component pins, aggregate four-cell pins, no derived literals, no cross-stack sum, v1 compatibility. Focused parity/refusal tests plus full suite. | Independent of U1/U2 |
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-moe-routing-energy.md:448:The current mechanism is `scripts/floor_mint_pinsets/mint1.json` plus `scripts/mint_floor_artifact_generalized.py`. It already embodies the right principle—plans supply hard pins and the mint compares rather than derives—but it remains structurally limited:
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-moe-routing-energy.md:973:| U3 — pinset v2 and multi-cell mint | `scripts/mint_floor_artifact_generalized.py`; `scripts/floor_mint_pinsets/schema_v2.json`; `joulewise/detection_floor.py`; `tests/test_mint_floor_artifact_generalized.py` | Decode and prefill metrics, per-plan component pins, aggregate four-cell pins, no derived literals, no cross-stack sum, v1 compatibility. Focused parity/refusal tests plus full suite. | Independent of U1/U2 |
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-moe-routing-energy.md:1792:The current mechanism is `scripts/floor_mint_pinsets/mint1.json` plus `scripts/mint_floor_artifact_generalized.py`. It already embodies the right principle—plans supply hard pins and the mint compares rather than derives—but it remains structurally limited:
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-moe-routing-energy.md:2123:| U3 — pinset v2 and multi-cell mint | `scripts/mint_floor_artifact_generalized.py`; `scripts/floor_mint_pinsets/schema_v2.json`; `joulewise/detection_floor.py`; `tests/test_mint_floor_artifact_generalized.py` | Decode and prefill metrics, per-plan component pins, aggregate four-cell pins, no derived literals, no cross-stack sum, v1 compatibility. Focused parity/refusal tests plus full suite. | Independent of U1/U2 |
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-energy-nutrition-label.md:1656:The current mechanism is `scripts/floor_mint_pinsets/mint1.json` plus `scripts/mint_floor_artifact_generalized.py`. It already embodies the right principle—plans supply hard pins and the mint compares rather than derives—but it remains structurally limited:
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-energy-nutrition-label.md:1813:| U3 — pinset v2 and multi-cell mint | `scripts/mint_floor_artifact_generalized.py`; `scripts/floor_mint_pinsets/schema_v2.json`; `joulewise/detection_floor.py`; `tests/test_mint_floor_artifact_generalized.py` | Decode and prefill metrics, per-plan component pins, aggregate four-cell pins, no derived literals, no cross-stack sum, v1 compatibility. Focused parity/refusal tests plus full suite. | Independent of U1/U2 |
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-split-inference-metrology.md:640:The current mechanism is `scripts/floor_mint_pinsets/mint1.json` plus `scripts/mint_floor_artifact_generalized.py`. It already embodies the right principle—plans supply hard pins and the mint compares rather than derives—but it remains structurally limited:
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-split-inference-metrology.md:963:| U3 — pinset v2 and multi-cell mint | `scripts/mint_floor_artifact_generalized.py`; `scripts/floor_mint_pinsets/schema_v2.json`; `joulewise/detection_floor.py`; `tests/test_mint_floor_artifact_generalized.py` | Decode and prefill metrics, per-plan component pins, aggregate four-cell pins, no derived literals, no cross-stack sum, v1 compatibility. Focused parity/refusal tests plus full suite. | Independent of U1/U2 |
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-split-inference-metrology.md:3070:The current mechanism is `scripts/floor_mint_pinsets/mint1.json` plus `scripts/mint_floor_artifact_generalized.py`. It already embodies the right principle—plans supply hard pins and the mint compares rather than derives—but it remains structurally limited:
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-split-inference-metrology.md:3595:| U3 — pinset v2 and multi-cell mint | `scripts/mint_floor_artifact_generalized.py`; `scripts/floor_mint_pinsets/schema_v2.json`; `joulewise/detection_floor.py`; `tests/test_mint_floor_artifact_generalized.py` | Decode and prefill metrics, per-plan component pins, aggregate four-cell pins, no derived literals, no cross-stack sum, v1 compatibility. Focused parity/refusal tests plus full suite. | Independent of U1/U2 |
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-split-inference-metrology.md:4158:The current mechanism is `scripts/floor_mint_pinsets/mint1.json` plus `scripts/mint_floor_artifact_generalized.py`. It already embodies the right principle—plans supply hard pins and the mint compares rather than derives—but it remains structurally limited:
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-open-explore-contrarian.md:2464:The current mechanism is `scripts/floor_mint_pinsets/mint1.json` plus `scripts/mint_floor_artifact_generalized.py`. It already embodies the right principle—plans supply hard pins and the mint compares rather than derives—but it remains structurally limited:
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-open-explore-contrarian.md:2795:| U3 — pinset v2 and multi-cell mint | `scripts/mint_floor_artifact_generalized.py`; `scripts/floor_mint_pinsets/schema_v2.json`; `joulewise/detection_floor.py`; `tests/test_mint_floor_artifact_generalized.py` | Decode and prefill metrics, per-plan component pins, aggregate four-cell pins, no derived literals, no cross-stack sum, v1 compatibility. Focused parity/refusal tests plus full suite. | Independent of U1/U2 |
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-kv-context-energy.md:725:The current mechanism is `scripts/floor_mint_pinsets/mint1.json` plus `scripts/mint_floor_artifact_generalized.py`. It already embodies the right principle—plans supply hard pins and the mint compares rather than derives—but it remains structurally limited:
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-kv-context-energy.md:1048:| U3 — pinset v2 and multi-cell mint | `scripts/mint_floor_artifact_generalized.py`; `scripts/floor_mint_pinsets/schema_v2.json`; `joulewise/detection_floor.py`; `tests/test_mint_floor_artifact_generalized.py` | Decode and prefill metrics, per-plan component pins, aggregate four-cell pins, no derived literals, no cross-stack sum, v1 compatibility. Focused parity/refusal tests plus full suite. | Independent of U1/U2 |
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-kv-context-energy.md:1671:The current mechanism is `scripts/floor_mint_pinsets/mint1.json` plus `scripts/mint_floor_artifact_generalized.py`. It already embodies the right principle—plans supply hard pins and the mint compares rather than derives—but it remains structurally limited:
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-kv-context-energy.md:1994:| U3 — pinset v2 and multi-cell mint | `scripts/mint_floor_artifact_generalized.py`; `scripts/floor_mint_pinsets/schema_v2.json`; `joulewise/detection_floor.py`; `tests/test_mint_floor_artifact_generalized.py` | Decode and prefill metrics, per-plan component pins, aggregate four-cell pins, no derived literals, no cross-stack sum, v1 compatibility. Focused parity/refusal tests plus full suite. | Independent of U1/U2 |
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-open-explore-registry.md:2551:The current mechanism is `scripts/floor_mint_pinsets/mint1.json` plus `scripts/mint_floor_artifact_generalized.py`. It already embodies the right principle—plans supply hard pins and the mint compares rather than derives—but it remains structurally limited:
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-open-explore-registry.md:2882:| U3 — pinset v2 and multi-cell mint | `scripts/mint_floor_artifact_generalized.py`; `scripts/floor_mint_pinsets/schema_v2.json`; `joulewise/detection_floor.py`; `tests/test_mint_floor_artifact_generalized.py` | Decode and prefill metrics, per-plan component pins, aggregate four-cell pins, no derived literals, no cross-stack sum, v1 compatibility. Focused parity/refusal tests plus full suite. | Independent of U1/U2 |
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-batch-concurrency-energy.md:1410:The current mechanism is `scripts/floor_mint_pinsets/mint1.json` plus `scripts/mint_floor_artifact_generalized.py`. It already embodies the right principle—plans supply hard pins and the mint compares rather than derives—but it remains structurally limited:
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-batch-concurrency-energy.md:1733:| U3 — pinset v2 and multi-cell mint | `scripts/mint_floor_artifact_generalized.py`; `scripts/floor_mint_pinsets/schema_v2.json`; `joulewise/detection_floor.py`; `tests/test_mint_floor_artifact_generalized.py` | Decode and prefill metrics, per-plan component pins, aggregate four-cell pins, no derived literals, no cross-stack sum, v1 compatibility. Focused parity/refusal tests plus full suite. | Independent of U1/U2 |
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-wall-meter-validation.md:1212:The current mechanism is `scripts/floor_mint_pinsets/mint1.json` plus `scripts/mint_floor_artifact_generalized.py`. It already embodies the right principle—plans supply hard pins and the mint compares rather than derives—but it remains structurally limited:
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-wall-meter-validation.md:1535:| U3 — pinset v2 and multi-cell mint | `scripts/mint_floor_artifact_generalized.py`; `scripts/floor_mint_pinsets/schema_v2.json`; `joulewise/detection_floor.py`; `tests/test_mint_floor_artifact_generalized.py` | Decode and prefill metrics, per-plan component pins, aggregate four-cell pins, no derived literals, no cross-stack sum, v1 compatibility. Focused parity/refusal tests plus full suite. | Independent of U1/U2 |
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-wall-meter-validation.md:3160:The current mechanism is `scripts/floor_mint_pinsets/mint1.json` plus `scripts/mint_floor_artifact_generalized.py`. It already embodies the right principle—plans supply hard pins and the mint compares rather than derives—but it remains structurally limited:
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-wall-meter-validation.md:3491:| U3 — pinset v2 and multi-cell mint | `scripts/mint_floor_artifact_generalized.py`; `scripts/floor_mint_pinsets/schema_v2.json`; `joulewise/detection_floor.py`; `tests/test_mint_floor_artifact_generalized.py` | Decode and prefill metrics, per-plan component pins, aggregate four-cell pins, no derived literals, no cross-stack sum, v1 compatibility. Focused parity/refusal tests plus full suite. | Independent of U1/U2 |
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-wall-meter-validation.md:3661:The current mechanism is `scripts/floor_mint_pinsets/mint1.json` plus `scripts/mint_floor_artifact_generalized.py`. It already embodies the right principle—plans supply hard pins and the mint compares rather than derives—but it remains structurally limited:
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-long-generation-dynamics.md:1896:The current mechanism is `scripts/floor_mint_pinsets/mint1.json` plus `scripts/mint_floor_artifact_generalized.py`. It already embodies the right principle—plans supply hard pins and the mint compares rather than derives—but it remains structurally limited:
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-long-generation-dynamics.md:2219:| U3 — pinset v2 and multi-cell mint | `scripts/mint_floor_artifact_generalized.py`; `scripts/floor_mint_pinsets/schema_v2.json`; `joulewise/detection_floor.py`; `tests/test_mint_floor_artifact_generalized.py` | Decode and prefill metrics, per-plan component pins, aggregate four-cell pins, no derived literals, no cross-stack sum, v1 compatibility. Focused parity/refusal tests plus full suite. | Independent of U1/U2 |
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-spec-decode-energy.md:2024:The current mechanism is `scripts/floor_mint_pinsets/mint1.json` plus `scripts/mint_floor_artifact_generalized.py`. It already embodies the right principle—plans supply hard pins and the mint compares rather than derives—but it remains structurally limited:
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-spec-decode-energy.md:2347:| U3 — pinset v2 and multi-cell mint | `scripts/mint_floor_artifact_generalized.py`; `scripts/floor_mint_pinsets/schema_v2.json`; `joulewise/detection_floor.py`; `tests/test_mint_floor_artifact_generalized.py` | Decode and prefill metrics, per-plan component pins, aggregate four-cell pins, no derived literals, no cross-stack sum, v1 compatibility. Focused parity/refusal tests plus full suite. | Independent of U1/U2 |
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-mvp-icpe-upgrade.md:932:The current mechanism is `scripts/floor_mint_pinsets/mint1.json` plus `scripts/mint_floor_artifact_generalized.py`. It already embodies the right principle—plans supply hard pins and the mint compares rather than derives—but it remains structurally limited:
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-mvp-icpe-upgrade.md:1255:| U3 — pinset v2 and multi-cell mint | `scripts/mint_floor_artifact_generalized.py`; `scripts/floor_mint_pinsets/schema_v2.json`; `joulewise/detection_floor.py`; `tests/test_mint_floor_artifact_generalized.py` | Decode and prefill metrics, per-plan component pins, aggregate four-cell pins, no derived literals, no cross-stack sum, v1 compatibility. Focused parity/refusal tests plus full suite. | Independent of U1/U2 |
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-attention-variant-energy.md:2197:The current mechanism is `scripts/floor_mint_pinsets/mint1.json` plus `scripts/mint_floor_artifact_generalized.py`. It already embodies the right principle—plans supply hard pins and the mint compares rather than derives—but it remains structurally limited:
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-attention-variant-energy.md:2520:| U3 — pinset v2 and multi-cell mint | `scripts/mint_floor_artifact_generalized.py`; `scripts/floor_mint_pinsets/schema_v2.json`; `joulewise/detection_floor.py`; `tests/test_mint_floor_artifact_generalized.py` | Decode and prefill metrics, per-plan component pins, aggregate four-cell pins, no derived literals, no cross-stack sum, v1 compatibility. Focused parity/refusal tests plus full suite. | Independent of U1/U2 |
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-open-explore-repo.md:1614:The current mechanism is `scripts/floor_mint_pinsets/mint1.json` plus `scripts/mint_floor_artifact_generalized.py`. It already embodies the right principle—plans supply hard pins and the mint compares rather than derives—but it remains structurally limited:
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-open-explore-repo.md:1937:| U3 — pinset v2 and multi-cell mint | `scripts/mint_floor_artifact_generalized.py`; `scripts/floor_mint_pinsets/schema_v2.json`; `joulewise/detection_floor.py`; `tests/test_mint_floor_artifact_generalized.py` | Decode and prefill metrics, per-plan component pins, aggregate four-cell pins, no derived literals, no cross-stack sum, v1 compatibility. Focused parity/refusal tests plus full suite. | Independent of U1/U2 |
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-open-explore-repo.md:4029:scripts/mint_floor_artifact_generalized.py
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-open-explore-repo.md:4075:tests/test_mint_floor_artifact_generalized.py
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-open-explore-repo.md:4552:tests/test_mint_floor_artifact_generalized.py:496:            "refusal_reasons": [],
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-open-explore-repo.md:4553:tests/test_mint_floor_artifact_generalized.py:508:        "spec_membership_refusals": [],
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-open-explore-repo.md:4554:tests/test_mint_floor_artifact_generalized.py:509:        "idle_admission_refusals": [],
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-open-explore-repo.md:4555:tests/test_mint_floor_artifact_generalized.py:1019:                    # The pinset-load refusal must fire on its own merits:
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-floor-methodology-general.md:706:| U3 — pinset v2 and multi-cell mint | `scripts/mint_floor_artifact_generalized.py`; `scripts/floor_mint_pinsets/schema_v2.json`; `joulewise/detection_floor.py`; `tests/test_mint_floor_artifact_generalized.py` | Decode and prefill metrics, per-plan component pins, aggregate four-cell pins, no derived literals, no cross-stack sum, v1 compatibility. Focused parity/refusal tests plus full suite. | Independent of U1/U2 |
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-floor-methodology-general.md:876:The current mechanism is `scripts/floor_mint_pinsets/mint1.json` plus `scripts/mint_floor_artifact_generalized.py`. It already embodies the right principle—plans supply hard pins and the mint compares rather than derives—but it remains structurally limited:
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-floor-methodology-general.md:3815:The current mechanism is `scripts/floor_mint_pinsets/mint1.json` plus `scripts/mint_floor_artifact_generalized.py`. It already embodies the right principle—plans supply hard pins and the mint compares rather than derives—but it remains structurally limited:
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-floor-methodology-general.md:4146:| U3 — pinset v2 and multi-cell mint | `scripts/mint_floor_artifact_generalized.py`; `scripts/floor_mint_pinsets/schema_v2.json`; `joulewise/detection_floor.py`; `tests/test_mint_floor_artifact_generalized.py` | Decode and prefill metrics, per-plan component pins, aggregate four-cell pins, no derived literals, no cross-stack sum, v1 compatibility. Focused parity/refusal tests plus full suite. | Independent of U1/U2 |
docs/process_traces/2026-08-07-d117-u-units/U3-FIX-CONTRACT.md:1:WRITE_SCOPE: ["scripts/mint_floor_artifact_generalized.py","scripts/floor_mint_pinsets/schema_v2.json","joulewise/detection_floor.py","tests/test_mint_floor_artifact_generalized.py"]
docs/process_traces/2026-08-07-d117-u-units/U1-AUDIT-EXEC.md:9446:   135	The current mechanism is `scripts/floor_mint_pinsets/mint1.json` plus `scripts/mint_floor_artifact_generalized.py`. It already embodies the right principle—plans supply hard pins and the mint compares rather than derives—but it remains structurally limited:
docs/process_traces/2026-08-07-d117-u-units/U1-AUDIT-EXEC.md:37040:4379:+docs/process_traces/2026-08-07-d117-plan-freeze/DESIGN-MEMO.md:458:| U3 — pinset v2 and multi-cell mint | `scripts/mint_floor_artifact_generalized.py`; `scripts/floor_mint_pinsets/schema_v2.json`; `joulewise/detection_floor.py`; `tests/test_mint_floor_artifact_generalized.py` | Decode and prefill metrics, per-plan component pins, aggregate four-cell pins, no derived literals, no cross-stack sum, v1 compatibility. Focused parity/refusal tests plus full suite. | Independent of U1/U2 |
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-contamination-characterization.md:2162:The current mechanism is `scripts/floor_mint_pinsets/mint1.json` plus `scripts/mint_floor_artifact_generalized.py`. It already embodies the right principle—plans supply hard pins and the mint compares rather than derives—but it remains structurally limited:
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-contamination-characterization.md:2489:| U3 — pinset v2 and multi-cell mint | `scripts/mint_floor_artifact_generalized.py`; `scripts/floor_mint_pinsets/schema_v2.json`; `joulewise/detection_floor.py`; `tests/test_mint_floor_artifact_generalized.py` | Decode and prefill metrics, per-plan component pins, aggregate four-cell pins, no derived literals, no cross-stack sum, v1 compatibility. Focused parity/refusal tests plus full suite. | Independent of U1/U2 |
docs/process_traces/2026-08-07-d117-u-units/U1-AUDIT-CONTRACT.md:185:docs/process_traces/2026-08-04-calbracket-integration-collision/RESOLUTION.md:18:   `scripts/mint_floor_artifact_generalized.py` to the D-109 signature
docs/process_traces/2026-08-07-d117-u-units/U1-AUDIT-CONTRACT.md:815:The current mechanism is `scripts/floor_mint_pinsets/mint1.json` plus `scripts/mint_floor_artifact_generalized.py`. It already embodies the right principle—plans supply hard pins and the mint compares rather than derives—but it remains structurally limited:
docs/process_traces/2026-08-07-d117-u-units/U1-AUDIT-CONTRACT.md:1139:| U3 — pinset v2 and multi-cell mint | `scripts/mint_floor_artifact_generalized.py`; `scripts/floor_mint_pinsets/schema_v2.json`; `joulewise/detection_floor.py`; `tests/test_mint_floor_artifact_generalized.py` | Decode and prefill metrics, per-plan component pins, aggregate four-cell pins, no derived literals, no cross-stack sum, v1 compatibility. Focused parity/refusal tests plus full suite. | Independent of U1/U2 |
docs/process_traces/2026-08-07-d117-u-units/U1-AUDIT-CONTRACT.md:11526:   135	The current mechanism is `scripts/floor_mint_pinsets/mint1.json` plus `scripts/mint_floor_artifact_generalized.py`. It already embodies the right principle—plans supply hard pins and the mint compares rather than derives—but it remains structurally limited:
docs/process_traces/2026-08-04-calbracket-collision-consult/consult-solhigh.md:33:        "location": "scripts/mint_floor_artifact_generalized.py:4"
docs/process_traces/2026-08-04-calbracket-collision-consult/consult-solhigh.md:152:- A multi-version interface pin adds negotiation machinery when the generalized tool loads exactly one local core file (`scripts/mint_floor_artifact_generalized.py:478-492`). Introduce versions only if simultaneous compatibility with multiple core revisions becomes a real requirement.
docs/process_traces/2026-08-04-calbracket-collision-consult/consult-solhigh.md:177:The mechanism at `scripts/mint_floor_artifact_generalized.py:82-110` freezes selected signatures, while `_fresh_original_core` loads whatever bytes currently occupy `scripts/mint_floor_artifact.py`. It is an exact, review-controlled compatibility-interface pin—not a byte freeze.
docs/process_traces/2026-08-04-calbracket-collision-consult/consult-solhigh.md:198:- `scripts/mint_floor_artifact_generalized.py`
docs/process_traces/2026-08-04-calbracket-collision-consult/consult-solhigh.md:203:- `tests/test_mint_floor_artifact_generalized.py`
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-EXEC.md:22: M scripts/mint_floor_artifact_generalized.py
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-EXEC.md:23: M tests/test_mint_floor_artifact_generalized.py
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-EXEC.md:1497:tests/test_mint_floor_artifact_generalized.py:40:MINT1_PINSET = REPO_ROOT / "scripts" / "floor_mint_pinsets" / "mint1.json"
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-EXEC.md:1498:tests/test_mint_floor_artifact_generalized.py:69:def write_pinset(root: Path, value: dict) -> tuple[Path, str]:
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-EXEC.md:1499:tests/test_mint_floor_artifact_generalized.py:70:    path = root / "pinset.json"
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-EXEC.md:1500:tests/test_mint_floor_artifact_generalized.py:78:def seven_b_pinset() -> dict:
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-EXEC.md:1501:tests/test_mint_floor_artifact_generalized.py:84:        "mint_tool_version": "joulewise.floor_mint.generalized.v1",
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-EXEC.md:1502:tests/test_mint_floor_artifact_generalized.py:796:    pinset = {
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-EXEC.md:1503:tests/test_mint_floor_artifact_generalized.py:823:    return pinset, inputs
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-EXEC.md:1504:tests/test_mint_floor_artifact_generalized.py:826:def freeze_synthetic_v2_pinset(
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-EXEC.md:1505:tests/test_mint_floor_artifact_generalized.py:829:    pinset, inputs = synthetic_v2_fixture()
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-EXEC.md:1506:tests/test_mint_floor_artifact_generalized.py:830:    draft_path, draft_sha256 = write_pinset(root, pinset)
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-EXEC.md:1507:tests/test_mint_floor_artifact_generalized.py:831:    parsed = generalized.load_pinset(draft_path, draft_sha256)
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-EXEC.md:1508:tests/test_mint_floor_artifact_generalized.py:834:        pinset=parsed,
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-EXEC.md:1509:tests/test_mint_floor_artifact_generalized.py:835:        pinset_path=draft_path,
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-EXEC.md:1510:tests/test_mint_floor_artifact_generalized.py:836:        pinset_sha256=draft_sha256,
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-EXEC.md:1511:tests/test_mint_floor_artifact_generalized.py:842:        pinset["producer_plans"],
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-EXEC.md:1512:tests/test_mint_floor_artifact_generalized.py:843:        pinset["aggregate"]["component_artifacts"],
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-EXEC.md:1513:tests/test_mint_floor_artifact_generalized.py:851:        for producer in pinset["producer_plans"]
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-EXEC.md:1514:tests/test_mint_floor_artifact_generalized.py:854:        pinset["aggregate"]["component_artifacts"], producer_hashes
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-EXEC.md:1515:tests/test_mint_floor_artifact_generalized.py:857:    pinset["aggregate"]["producer_set_sha256"] = (
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-EXEC.md:1516:tests/test_mint_floor_artifact_generalized.py:858:        generalized._canonical_json_sha256(pinset["producer_plans"])
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-EXEC.md:1517:tests/test_mint_floor_artifact_generalized.py:860:    path, digest = write_pinset(root, pinset)
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-EXEC.md:1518:tests/test_mint_floor_artifact_generalized.py:865:    def test_mint1_pinset_is_exactly_the_original_hard_pin_set(self) -> None:
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-EXEC.md:1519:tests/test_mint_floor_artifact_generalized.py:866:        pinset = generalized.load_pinset(
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-EXEC.md:1520:tests/test_mint_floor_artifact_generalized.py:869:        self.assertEqual(pinset.plan.sha256, mint1.PLAN_SHA256)
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-EXEC.md:1521:tests/test_mint_floor_artifact_generalized.py:870:        self.assertEqual(pinset.artifact.cell_id, mint1.CELL_ID)
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-EXEC.md:1522:tests/test_mint_floor_artifact_generalized.py:872:            pinset.absolute.evaluation_basis_sha256,
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-EXEC.md:1523:tests/test_mint_floor_artifact_generalized.py:876:            pinset.comparative.evaluation_basis_sha256,
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-EXEC.md:1524:tests/test_mint_floor_artifact_generalized.py:880:            pinset.cell.operative_floor_six_decimal,
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-EXEC.md:1525:tests/test_mint_floor_artifact_generalized.py:884:    def test_pinset_digest_mismatch_refuses(self) -> None:
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-EXEC.md:1526:tests/test_mint_floor_artifact_generalized.py:886:            generalized.load_pinset(MINT1_PINSET, "0" * 64)
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-EXEC.md:1527:tests/test_mint_floor_artifact_generalized.py:888:    def test_pinset_missing_or_extra_fields_refuse(self) -> None:
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-EXEC.md:1528:tests/test_mint_floor_artifact_generalized.py:901:                    path, digest = write_pinset(root, value)
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-EXEC.md:1529:tests/test_mint_floor_artifact_generalized.py:905:                        generalized.load_pinset(path, digest)
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-EXEC.md:1530:tests/test_mint_floor_artifact_generalized.py:911:            path, digest = write_pinset(Path(tmp), value)
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-EXEC.md:1531:tests/test_mint_floor_artifact_generalized.py:915:                generalized.load_pinset(path, digest)
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-EXEC.md:1532:tests/test_mint_floor_artifact_generalized.py:917:    def test_pinset_cannot_weaken_fixed_decode_contract(self) -> None:
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-EXEC.md:1533:tests/test_mint_floor_artifact_generalized.py:932:                    path, digest = write_pinset(root, value)
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-EXEC.md:1534:tests/test_mint_floor_artifact_generalized.py:936:                        generalized.load_pinset(path, digest)
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-EXEC.md:1535:tests/test_mint_floor_artifact_generalized.py:968:            REPO_ROOT / "scripts" / "floor_mint_pinsets" / "schema_v2.json"
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-EXEC.md:1536:tests/test_mint_floor_artifact_generalized.py:979:            path, digest = write_pinset(Path(tmp), desk)
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-EXEC.md:1537:tests/test_mint_floor_artifact_generalized.py:983:                generalized.load_pinset(path, digest)
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-EXEC.md:1538:tests/test_mint_floor_artifact_generalized.py:987:            path, digest, inputs = freeze_synthetic_v2_pinset(Path(tmp))
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-EXEC.md:1539:tests/test_mint_floor_artifact_generalized.py:989:                pinset_path=path,
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-EXEC.md:1540:tests/test_mint_floor_artifact_generalized.py:990:                pinset_sha256=digest,
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-EXEC.md:1541:tests/test_mint_floor_artifact_generalized.py:998:                    pinset_path=path,
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-EXEC.md:1542:tests/test_mint_floor_artifact_generalized.py:999:                    pinset_sha256=digest,
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-EXEC.md:1543:tests/test_mint_floor_artifact_generalized.py:1021:            path, digest, _inputs = freeze_synthetic_v2_pinset(root)
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-EXEC.md:1544:tests/test_mint_floor_artifact_generalized.py:1026:                        "--pinset",
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-EXEC.md:1545:tests/test_mint_floor_artifact_generalized.py:1028:                        "--pinset-sha256",
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-EXEC.md:1546:tests/test_mint_floor_artifact_generalized.py:1046:            path, _digest, _inputs = freeze_synthetic_v2_pinset(root)
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-EXEC.md:1547:tests/test_mint_floor_artifact_generalized.py:1066:                    candidate_path, candidate_digest = write_pinset(
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-EXEC.md:1548:tests/test_mint_floor_artifact_generalized.py:1070:                        generalized.load_pinset(
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-EXEC.md:1549:tests/test_mint_floor_artifact_generalized.py:1077:            path, _digest, _inputs = freeze_synthetic_v2_pinset(root)
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-EXEC.md:1550:tests/test_mint_floor_artifact_generalized.py:1115:                    candidate_path, candidate_digest = write_pinset(
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-EXEC.md:1551:tests/test_mint_floor_artifact_generalized.py:1119:                        generalized.load_pinset(
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-EXEC.md:1552:tests/test_mint_floor_artifact_generalized.py:1126:            path, _digest, _inputs = freeze_synthetic_v2_pinset(root)
tests/test_mint_floor_artifact.py:1096:                    "load_calibration_ledger_snapshot",
tests/test_calibration_bracketing.py:40:    load_calibration_ledger_snapshot,
tests/test_calibration_bracketing.py:643:                require_committed_pin=False,
tests/test_calibration_bracketing.py:685:            snapshot = load_calibration_ledger_snapshot(
tests/test_calibration_bracketing.py:690:                require_committed_pin=True,
tests/test_calibration_ledger.py:51:    load_calibration_ledger_snapshot,
tests/test_calibration_ledger.py:176:            require_committed_pin=False,
tests/test_calibration_ledger.py:193:        return load_calibration_ledger_snapshot(
tests/test_calibration_ledger.py:198:            require_committed_pin=False,
tests/test_calibration_ledger.py:329:                require_committed_pin=False,
tests/test_calibration_ledger.py:422:        snapshot = load_calibration_ledger_snapshot(
tests/test_calibration_ledger.py:427:            require_committed_pin=False,
tests/test_calibration_ledger.py:846:                require_committed_pin=False,
tests/test_calibration_ledger.py:858:                require_committed_pin=False,
tests/test_calibration_ledger.py:897:                require_committed_pin=False,
tests/test_calibration_ledger.py:915:                require_committed_pin=False,
tests/test_calibration_ledger.py:940:                    require_committed_pin=False,
tests/test_calibration_ledger.py:962:                    require_committed_pin=False,
tests/test_calibration_ledger.py:994:                    require_committed_pin=False,
tests/test_calibration_ledger.py:1011:                require_committed_pin=False,
tests/test_calibration_ledger.py:1026:                require_committed_pin=False,
tests/test_calibration_ledger.py:1164:                    require_committed_pin=False,
tests/test_calibration_ledger.py:1207:                        require_committed_pin=False,
tests/test_calibration_ledger.py:1279:                require_committed_pin=False,
tests/test_calibration_ledger.py:1317:    require_committed_pin=False,
tests/test_calibration_ledger.py:1330:            require_committed_pin=False,
tests/test_calibration_ledger.py:1363:                    require_committed_pin=False,
tests/test_calibration_ledger.py:1379:            require_committed_pin=False,
tests/test_calibration_ledger.py:1382:        snapshot = load_calibration_ledger_snapshot(
tests/test_calibration_ledger.py:1385:            require_committed_pin=False,

codex
The reproduced combined mutation is refused before construction, and isolated probes for all nine fields each return a reason containing that field’s exact name. The three requested suites are green: focused 39, v1 parity 34, shared callers 249. I’m completing the trust-boundary and FIX-6b/8 assessment, then I’ll report a single CLEAN/BLOCK conclusion with the exact tails.
exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/joulewise-u3-reaudit-pycache python3 - <<'PY'
import copy, tempfile
from dataclasses import replace
from pathlib import Path
from scripts import mint_floor_artifact_generalized as g
from tests.test_mint_floor_artifact_generalized import (
    freeze_synthetic_v2_pinset, load_json, write_pinset,
    _repair_v2_pinset_self_hashes, _fixture_artifact_sha256,
)
with tempfile.TemporaryDirectory(dir='/tmp') as tmp:
    root = Path(tmp)
    path, _digest, inputs, snapshot = freeze_synthetic_v2_pinset(root)
    pinset = load_json(path)
    producer = pinset['producer_plans'][0]
    plan_id = producer['plan']['plan_id']
    source = inputs[plan_id]
    changed_full = '6.294381135190098'
    changed_six = '6.294381'
    producer['cells'][0]['postcollection']['absolute_floor_full_precision'] = changed_full
    producer['cells'][0]['postcollection']['absolute_floor_six_decimal'] = changed_six
    report = copy.deepcopy(source.cells['decode'].absolute.report)
    record = next(row for row in report['floor_mint_postcollection']['cells'] if row['cell_id'] == producer['cells'][0]['cell_id'])
    record['absolute_floor_full_precision'] = changed_full
    record['absolute_floor_six_decimal'] = changed_six
    report_sha = _fixture_artifact_sha256(report)
    for cell_pin in producer['cells']:
        cell_pin['postcollection']['extraction_report_sha256'] = report_sha
    updated = {}
    for role, components in source.cells.items():
        abs_cell = copy.deepcopy(components.absolute.cell)
        if role == 'decode':
            abs_cell['floor']['drift_widened_guarded_floor_j'] = float(changed_full)
        updated[role] = g.V2CellComponents(
            absolute=replace(components.absolute, report=report, report_sha256=report_sha, cell=abs_cell),
            comparative=replace(components.comparative, report=report, report_sha256=report_sha),
            allowed_consumer_condition_families=components.allowed_consumer_condition_families,
        )
    candidate_inputs = {**inputs, plan_id: replace(source, cells=updated)}
    _repair_v2_pinset_self_hashes(pinset)
    candidate_path, candidate_digest = write_pinset(root, pinset)
    try:
        g.mint_multi_cell_authenticated_artifact(
            pinset_path=candidate_path,
            pinset_sha256=candidate_digest,
            producer_inputs=candidate_inputs,
            calibration_ledger_snapshot=snapshot,
            project_commit='0' * 40,
            project_tree_state='clean',
        )
    except g.MintError as exc:
        print('coordinated_full_report_and_pin: REFUSED:', exc)
    else:
        print('coordinated_full_report_and_pin: MINTED')
PY" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u3
 succeeded in 499ms:
coordinated_full_report_and_pin: REFUSED: aggregate/component hash mismatch: component artifact 0 expected b0404c15df0b2e0afb445ab6cea9b2c08a7922e3d49fd7354b8aec05262d9851, observed 184f003f738bb6f5d45aa4983394be380425bafe052b65a15491739dcbb37230

exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/joulewise-u3-reaudit-pycache python3 - <<'PY'
import copy, tempfile
from dataclasses import replace
from pathlib import Path
from scripts import mint_floor_artifact_generalized as g
from tests.test_mint_floor_artifact_generalized import (
    freeze_synthetic_v2_pinset, load_json, write_pinset,
    _repair_v2_pinset_self_hashes, _fixture_artifact_sha256,
)
with tempfile.TemporaryDirectory(dir='/tmp') as tmp:
    root = Path(tmp)
    path, _digest, inputs, snapshot = freeze_synthetic_v2_pinset(root)
    pinset = load_json(path)
    producer = pinset['producer_plans'][0]
    plan_id = producer['plan']['plan_id']
    source = inputs[plan_id]
    changed_full = '6.294381135190098'
    changed_six = '6.294381'
    producer['cells'][0]['postcollection']['absolute_floor_full_precision'] = changed_full
    producer['cells'][0]['postcollection']['absolute_floor_six_decimal'] = changed_six
    report = copy.deepcopy(source.cells['decode'].absolute.report)
    record = next(row for row in report['floor_mint_postcollection']['cells'] if row['cell_id'] == producer['cells'][0]['cell_id'])
    record['absolute_floor_full_precision'] = changed_full
    record['absolute_floor_six_decimal'] = changed_six
    report_sha = _fixture_artifact_sha256(report)
    for cell_pin in producer['cells']:
        cell_pin['postcollection']['extraction_report_sha256'] = report_sha
    updated = {}
    for role, components in source.cells.items():
        abs_cell = copy.deepcopy(components.absolute.cell)
        if role == 'decode':
            abs_cell['floor']['drift_widened_guarded_floor_j'] = float(changed_full)
        updated[role] = g.V2CellComponents(
            absolute=replace(components.absolute, report=report, report_sha256=report_sha, cell=abs_cell),
            comparative=replace(components.comparative, report=report, report_sha256=report_sha),
            allowed_consumer_condition_families=components.allowed_consumer_condition_families,
        )
    candidate_inputs = {**inputs, plan_id: replace(source, cells=updated)}
    _repair_v2_pinset_self_hashes(pinset)
    draft_path, draft_digest = write_pinset(root, pinset)
    loaded = g.load_pinset(draft_path, draft_digest)
    _artifact, components = g._build_v2_artifacts(
        pinset=loaded,
        pinset_path=draft_path,
        pinset_sha256=draft_digest,
        producer_inputs=candidate_inputs,
        calibration_ledger_snapshot=snapshot,
        project_commit='0' * 40,
        project_tree_state='clean',
    )
    for producer_pin, entry, component in zip(pinset['producer_plans'], pinset['aggregate']['component_artifacts'], components):
        component_sha = _fixture_artifact_sha256(component)
        producer_pin['component_artifact']['sha256'] = component_sha
        entry['sha256'] = component_sha
    _repair_v2_pinset_self_hashes(pinset)
    final_path, final_digest = write_pinset(root, pinset)
    try:
        g.mint_multi_cell_authenticated_artifact(
            pinset_path=final_path,
            pinset_sha256=final_digest,
            producer_inputs=candidate_inputs,
            calibration_ledger_snapshot=snapshot,
            project_commit='0' * 40,
            project_tree_state='clean',
        )
    except g.MintError as exc:
        print('coordinated_report_pin_and_all_pinset_hashes: REFUSED:', exc)
    else:
        print('coordinated_report_pin_and_all_pinset_hashes: MINTED')
PY" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u3
 succeeded in 669ms:
coordinated_report_pin_and_all_pinset_hashes: REFUSED: constructed v2 artifact is invalid: cells[cell-0-decode]: absolute full-precision pin mismatch

2026-08-07T20:26:02.216672Z ERROR codex_models_manager::manager: failed to renew cache TTL: missing field `base_instructions` at line 94 column 5
exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/joulewise-u3-reaudit-pycache python3 - <<'PY'
import copy, io, tempfile
from pathlib import Path
from unittest import mock
from scripts import mint_floor_artifact_generalized as g
from tests.test_mint_floor_artifact_generalized import (
    install_v2_cli_fixture, load_json, write_pinset, _repair_v2_pinset_self_hashes,
)
with tempfile.TemporaryDirectory(dir='/tmp') as tmp:
    root = Path(tmp)
    source_path, _source_digest, manifest_path, load_test_core = install_v2_cli_fixture(root)
    candidate = load_json(source_path)
    replacements = {
        'pre_receipt_sha256': '0' * 64,
        'pre_content_sha256': '1' * 64,
        'post_receipt_sha256': '2' * 64,
        'post_content_sha256': '3' * 64,
        'bracket_binding_sha256': '4' * 64,
        'terminal_ledger_head_sha256': '5' * 64,
        'extraction_report_sha256': '6' * 64,
        'observed_drift_s': '0.012000',
        'applied_allowance_s': '0.012000',
    }
    for cell in candidate['producer_plans'][0]['cells']:
        cell['postcollection'].update(replacements)
    _repair_v2_pinset_self_hashes(candidate)
    path, digest = write_pinset(root, candidate)
    stderr = io.StringIO()
    with mock.patch.object(g, '_fresh_original_core', side_effect=load_test_core), mock.patch('sys.stderr', stderr):
        exit_code = g.main([
            '--pinset', str(path), '--pinset-sha256', digest,
            '--v2-input-manifest', str(manifest_path),
            '--out', str(root / 'floor.json'),
            '--single-count-out', str(root / 'single-count.txt'),
            '--project-commit', '0' * 40,
            '--project-tree-state', 'clean',
        ])
    print('production_cli_combined_exit=', exit_code)
    print('production_cli_combined_reason=', stderr.getvalue().strip())
    print('floor_written=', (root / 'floor.json').exists())
    print('single_count_written=', (root / 'single-count.txt').exists())
PY" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u3
 succeeded in 449ms:
production_cli_combined_exit= 2
production_cli_combined_reason= error: postcollection_evidence_mismatch: bracket_binding_sha256 mismatch against supplied bracket-binding artifact bytes
floor_written= False
single_count_written= False

exec
/bin/zsh -lc 'git diff --check origin/main...HEAD; git status --short --branch; git rev-parse HEAD' in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u3
 succeeded in 0ms:
## impl/d117-u3-pinset-v2...origin/impl/d117-u3-pinset-v2
454f77795f5ed2f1841055a7ce125e1456f583de

codex
## Verdict

CLEAN — the charged authentication class is closed at `454f77795f5ed2f1841055a7ce125e1456f583de`. The escalation trigger does not fire.

### 1. Per-field equality disposition

| Pinned field | Result | Evidence source |
|---|---|---|
| `pre_receipt_sha256` | Equality-compared; not presence-only | Authenticated ledger pre-observation |
| `pre_content_sha256` | Equality-compared; not presence-only | Authenticated ledger pre-observation |
| `post_receipt_sha256` | Equality-compared; not presence-only | Authenticated ledger post-observation |
| `post_content_sha256` | Equality-compared; not presence-only | Authenticated ledger post-observation |
| `bracket_binding_sha256` | Equality-compared; not presence-only | SHA-256 of supplied binding bytes |
| `terminal_ledger_head_sha256` | Equality-compared; not presence-only | Ledger-bound terminal head |
| `extraction_report_sha256` | Equality-compared for both component reports; not presence-only | SHA-256 of supplied report bytes |
| `observed_drift_s` | Equality-compared; not presence-only | Decimal difference between authenticated ledger endpoints |
| `applied_allowance_s` | Equality-compared; not presence-only | Extraction-report record; also independently constrained by the fixed allowance rule |

Support: [scripts/mint_floor_artifact_generalized.py:2069](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u3/scripts/mint_floor_artifact_generalized.py:2069), [scripts/mint_floor_artifact_generalized.py:2081](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u3/scripts/mint_floor_artifact_generalized.py:2081), [scripts/mint_floor_artifact_generalized.py:2095](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u3/scripts/mint_floor_artifact_generalized.py:2095), [scripts/mint_floor_artifact_generalized.py:2116](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u3/scripts/mint_floor_artifact_generalized.py:2116), [scripts/mint_floor_artifact_generalized.py:2122](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u3/scripts/mint_floor_artifact_generalized.py:2122), [scripts/mint_floor_artifact_generalized.py:2143](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u3/scripts/mint_floor_artifact_generalized.py:2143).

### 2. Original scenario

Replacing every custody hash, changing drift and allowance, and repairing the pinset self-hashes now returns exit code 2 and writes neither output. The combined production-CLI probe stops on the named `bracket_binding_sha256` mismatch.

Isolated probes confirmed named reasons for all nine fields: `pre_receipt_sha256`, `pre_content_sha256`, `post_receipt_sha256`, `post_content_sha256`, `bracket_binding_sha256`, `terminal_ledger_head_sha256`, `extraction_report_sha256`, `observed_drift_s`, and `applied_allowance_s`.

### 3. Evidence authentication

The production path does not accept arbitrary evidence solely because the operator supplies its path:

- Calibration acceptance has an exact byte hash pinned in code: [joulewise/calibration_bracketing.py:431](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u3/joulewise/calibration_bracketing.py:431).
- The ledger validates its receipt hash chain, requires the head-pin bytes to match Git `HEAD`, enforces the acceptance cutoff, and rehashes custody artifacts: [joulewise/calibration_ledger.py:637](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u3/joulewise/calibration_ledger.py:637).
- Binding endpoints are resolved against that ledger snapshot: [scripts/mint_floor_artifact_generalized.py:1779](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u3/scripts/mint_floor_artifact_generalized.py:1779).
- Reports are checked against strict-validated source bundles, bundle/config hashes, source metrics and widths, and rederived allowance evidence: [scripts/mint_floor_artifact.py:1012](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u3/scripts/mint_floor_artifact.py:1012).

This is digest-, Git-, custody-, and rederivation-based authentication, not digital-signature authentication. If the Git head pin and full ledger history are outside the trusted boundary, origin is not established; that limitation is explicit at [joulewise/calibration_ledger.py:647](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u3/joulewise/calibration_ledger.py:647). Within the implemented trust model, the equality checks do not merely transfer authority to arbitrary operator-supplied files.

### 4. FIX-6b and FIX-8

FIX-6b: a coordinated report-and-pin change does not pass with unchanged source evidence. A stronger probe also changed the report floor field and regenerated the report, component, producer, aggregate, and pinset hashes; final validation refused with the named absolute full-precision mismatch. The reconstructed artifact is compared against the pins at [scripts/mint_floor_artifact_generalized.py:2657](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u3/scripts/mint_floor_artifact_generalized.py:2657).

FIX-8: yes, the test calls the real `main()` entry-point logic and traverses v2 manifest authentication, minting, binding, and exclusive output dispatch: [tests/test_mint_floor_artifact_generalized.py:1891](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u3/tests/test_mint_floor_artifact_generalized.py:1891), [scripts/mint_floor_artifact_generalized.py:3319](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u3/scripts/mint_floor_artifact_generalized.py:3319). It invokes `main()` directly rather than as a subprocess and substitutes a file-checking test adapter for the underlying acceptance/ledger/component core, so it is a real CLI orchestration test but not an unmocked live-evidence test. Its component hashes are fixed independent golden constants.

### 5. Same-signature statement

No — the self-attestation/presence-only class does not survive in the reachable production CLI path. Every charged field has an evidence equality check, the referenced evidence is independently constrained by the ledger/source-data authentication chain, and the reproduced scenario refuses with per-field names.

The lower-level authenticated-input helper trusts its caller to supply already-authenticated objects, but it has no non-test call site and still performs the field comparisons. Production enters through the file-authenticating path.

Checks performed: HEAD and clean status verification; round-2 diff review; per-field and combined mutation probes; stronger coordinated report/pin/hash probe; focused suite; v1 parity suite; shared-caller set; `git diff --check`. No repository files were modified.

Exact focused tail:

```text
test_v2_decimal_pins_require_plain_unsigned_strings (tests.test_mint_floor_artifact_generalized.V2PinsetAndMintTests.test_v2_decimal_pins_require_plain_unsigned_strings) ... ok
test_v2_input_manifest_routes_all_authenticated_evidence_files (tests.test_mint_floor_artifact_generalized.V2PinsetAndMintTests.test_v2_input_manifest_routes_all_authenticated_evidence_files) ... ok
test_v2_mint_does_not_render_or_round_floor_literals (tests.test_mint_floor_artifact_generalized.V2PinsetAndMintTests.test_v2_mint_does_not_render_or_round_floor_literals) ... ok

----------------------------------------------------------------------
Ran 39 tests in 2.271s

OK
```

Exact v1-parity tail:

```text
test_required_stack_fields_remain_fail_closed (tests.test_mint_floor_artifact.StackIdentityParityTests.test_required_stack_fields_remain_fail_closed) ... ok
test_sampler_is_required_on_both_mint_and_claim_sides (tests.test_mint_floor_artifact.StackIdentityParityTests.test_sampler_is_required_on_both_mint_and_claim_sides) ... ok
test_windows_tokenizer_path_normalizes_like_mint (tests.test_mint_floor_artifact.StackIdentityParityTests.test_windows_tokenizer_path_normalizes_like_mint) ... ok

----------------------------------------------------------------------
Ran 34 tests in 0.620s

OK
```

Exact shared-caller tail:

```text
test_v4_valid_exact_plus_corrupted_same_bundle_clone_refuses (tests.test_analysis_integration.SupersessionAwareCooldownJoinTests.test_v4_valid_exact_plus_corrupted_same_bundle_clone_refuses) ... ok
test_valid_supersession_resolves_selected_occurrence (tests.test_analysis_integration.SupersessionAwareCooldownJoinTests.test_valid_supersession_resolves_selected_occurrence) ... ok
test_validated_log_supersession_selects_governing_cooldown_row (tests.test_analysis_integration.SupersessionAwareCooldownJoinTests.test_validated_log_supersession_selects_governing_cooldown_row) ... ok

----------------------------------------------------------------------
Ran 249 tests in 25.737s

OK
```
tokens used
205,602
## Verdict

CLEAN — the charged authentication class is closed at `454f77795f5ed2f1841055a7ce125e1456f583de`. The escalation trigger does not fire.

### 1. Per-field equality disposition

| Pinned field | Result | Evidence source |
|---|---|---|
| `pre_receipt_sha256` | Equality-compared; not presence-only | Authenticated ledger pre-observation |
| `pre_content_sha256` | Equality-compared; not presence-only | Authenticated ledger pre-observation |
| `post_receipt_sha256` | Equality-compared; not presence-only | Authenticated ledger post-observation |
| `post_content_sha256` | Equality-compared; not presence-only | Authenticated ledger post-observation |
| `bracket_binding_sha256` | Equality-compared; not presence-only | SHA-256 of supplied binding bytes |
| `terminal_ledger_head_sha256` | Equality-compared; not presence-only | Ledger-bound terminal head |
| `extraction_report_sha256` | Equality-compared for both component reports; not presence-only | SHA-256 of supplied report bytes |
| `observed_drift_s` | Equality-compared; not presence-only | Decimal difference between authenticated ledger endpoints |
| `applied_allowance_s` | Equality-compared; not presence-only | Extraction-report record; also independently constrained by the fixed allowance rule |

Support: [scripts/mint_floor_artifact_generalized.py:2069](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u3/scripts/mint_floor_artifact_generalized.py:2069), [scripts/mint_floor_artifact_generalized.py:2081](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u3/scripts/mint_floor_artifact_generalized.py:2081), [scripts/mint_floor_artifact_generalized.py:2095](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u3/scripts/mint_floor_artifact_generalized.py:2095), [scripts/mint_floor_artifact_generalized.py:2116](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u3/scripts/mint_floor_artifact_generalized.py:2116), [scripts/mint_floor_artifact_generalized.py:2122](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u3/scripts/mint_floor_artifact_generalized.py:2122), [scripts/mint_floor_artifact_generalized.py:2143](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u3/scripts/mint_floor_artifact_generalized.py:2143).

### 2. Original scenario

Replacing every custody hash, changing drift and allowance, and repairing the pinset self-hashes now returns exit code 2 and writes neither output. The combined production-CLI probe stops on the named `bracket_binding_sha256` mismatch.

Isolated probes confirmed named reasons for all nine fields: `pre_receipt_sha256`, `pre_content_sha256`, `post_receipt_sha256`, `post_content_sha256`, `bracket_binding_sha256`, `terminal_ledger_head_sha256`, `extraction_report_sha256`, `observed_drift_s`, and `applied_allowance_s`.

### 3. Evidence authentication

The production path does not accept arbitrary evidence solely because the operator supplies its path:

- Calibration acceptance has an exact byte hash pinned in code: [joulewise/calibration_bracketing.py:431](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u3/joulewise/calibration_bracketing.py:431).
- The ledger validates its receipt hash chain, requires the head-pin bytes to match Git `HEAD`, enforces the acceptance cutoff, and rehashes custody artifacts: [joulewise/calibration_ledger.py:637](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u3/joulewise/calibration_ledger.py:637).
- Binding endpoints are resolved against that ledger snapshot: [scripts/mint_floor_artifact_generalized.py:1779](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u3/scripts/mint_floor_artifact_generalized.py:1779).
- Reports are checked against strict-validated source bundles, bundle/config hashes, source metrics and widths, and rederived allowance evidence: [scripts/mint_floor_artifact.py:1012](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u3/scripts/mint_floor_artifact.py:1012).

This is digest-, Git-, custody-, and rederivation-based authentication, not digital-signature authentication. If the Git head pin and full ledger history are outside the trusted boundary, origin is not established; that limitation is explicit at [joulewise/calibration_ledger.py:647](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u3/joulewise/calibration_ledger.py:647). Within the implemented trust model, the equality checks do not merely transfer authority to arbitrary operator-supplied files.

### 4. FIX-6b and FIX-8

FIX-6b: a coordinated report-and-pin change does not pass with unchanged source evidence. A stronger probe also changed the report floor field and regenerated the report, component, producer, aggregate, and pinset hashes; final validation refused with the named absolute full-precision mismatch. The reconstructed artifact is compared against the pins at [scripts/mint_floor_artifact_generalized.py:2657](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u3/scripts/mint_floor_artifact_generalized.py:2657).

FIX-8: yes, the test calls the real `main()` entry-point logic and traverses v2 manifest authentication, minting, binding, and exclusive output dispatch: [tests/test_mint_floor_artifact_generalized.py:1891](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u3/tests/test_mint_floor_artifact_generalized.py:1891), [scripts/mint_floor_artifact_generalized.py:3319](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u3/scripts/mint_floor_artifact_generalized.py:3319). It invokes `main()` directly rather than as a subprocess and substitutes a file-checking test adapter for the underlying acceptance/ledger/component core, so it is a real CLI orchestration test but not an unmocked live-evidence test. Its component hashes are fixed independent golden constants.

### 5. Same-signature statement

No — the self-attestation/presence-only class does not survive in the reachable production CLI path. Every charged field has an evidence equality check, the referenced evidence is independently constrained by the ledger/source-data authentication chain, and the reproduced scenario refuses with per-field names.

The lower-level authenticated-input helper trusts its caller to supply already-authenticated objects, but it has no non-test call site and still performs the field comparisons. Production enters through the file-authenticating path.

Checks performed: HEAD and clean status verification; round-2 diff review; per-field and combined mutation probes; stronger coordinated report/pin/hash probe; focused suite; v1 parity suite; shared-caller set; `git diff --check`. No repository files were modified.

Exact focused tail:

```text
test_v2_decimal_pins_require_plain_unsigned_strings (tests.test_mint_floor_artifact_generalized.V2PinsetAndMintTests.test_v2_decimal_pins_require_plain_unsigned_strings) ... ok
test_v2_input_manifest_routes_all_authenticated_evidence_files (tests.test_mint_floor_artifact_generalized.V2PinsetAndMintTests.test_v2_input_manifest_routes_all_authenticated_evidence_files) ... ok
test_v2_mint_does_not_render_or_round_floor_literals (tests.test_mint_floor_artifact_generalized.V2PinsetAndMintTests.test_v2_mint_does_not_render_or_round_floor_literals) ... ok

----------------------------------------------------------------------
Ran 39 tests in 2.271s

OK
```

Exact v1-parity tail:

```text
test_required_stack_fields_remain_fail_closed (tests.test_mint_floor_artifact.StackIdentityParityTests.test_required_stack_fields_remain_fail_closed) ... ok
test_sampler_is_required_on_both_mint_and_claim_sides (tests.test_mint_floor_artifact.StackIdentityParityTests.test_sampler_is_required_on_both_mint_and_claim_sides) ... ok
test_windows_tokenizer_path_normalizes_like_mint (tests.test_mint_floor_artifact.StackIdentityParityTests.test_windows_tokenizer_path_normalizes_like_mint) ... ok

----------------------------------------------------------------------
Ran 34 tests in 0.620s

OK
```

Exact shared-caller tail:

```text
test_v4_valid_exact_plus_corrupted_same_bundle_clone_refuses (tests.test_analysis_integration.SupersessionAwareCooldownJoinTests.test_v4_valid_exact_plus_corrupted_same_bundle_clone_refuses) ... ok
test_valid_supersession_resolves_selected_occurrence (tests.test_analysis_integration.SupersessionAwareCooldownJoinTests.test_valid_supersession_resolves_selected_occurrence) ... ok
test_validated_log_supersession_selects_governing_cooldown_row (tests.test_analysis_integration.SupersessionAwareCooldownJoinTests.test_validated_log_supersession_selects_governing_cooldown_row) ... ok

----------------------------------------------------------------------
Ran 249 tests in 25.737s

OK
```
