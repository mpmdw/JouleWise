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
session id: 019fde17-30a0-70c0-8b35-1ffc87904a7f
--------
user
PAPER §5 REFUSAL-RECORD INTEGRATION DRAFT (read-only; no writes; final message = the prose + placement). The refusal census (docs/process_traces/2026-08-07-meta-sweeps/REFUSAL-CENSUS.md) produced a paper-ready table in its §5. The MVP paper docs/paper/draft-v1.md §5 currently makes QUALITATIVE claims about the refusal log ('The refusal log is part of the evaluation, not an embarrassment to omit...'). Draft the integration.
REQUIREMENTS: (1) use the census's EXACT verified numbers, and honor the two-denominator distinction — occurrence-level reconstructability is 14 of 44 (31.8%) and identity-level is 13 of 38 (34.2%); these are DIFFERENT denominators and neither derives from the other (a magistrate overstatement was already corrected on this exact point — do not reintroduce it); (2) the honest framing the census itself reached: the logs prove refusals happened far more reliably than they explain why each member was refused — this is a LIMITATION the paper should own, not hide, and it motivates the reason-code work; (3) plain advisor-facing language, matching the draft's voice — no internal vocabulary, no decision IDs; (4) state clearly that these counts describe the instrument's development history, and that the three prospective windows will add to this record; (5) respect the draft-status convention (values that are final now are stated; anything pending keeps a bracketed marker).
DELIVER: the exact replacement/addition prose for §5 with insertion points named by their current sentences, a compact table sized for a 2-column paper, and a note on what would need updating after the three windows.
codex
I’ll inspect the census §5 and the paper’s current §5, then return only advisor-facing integration prose, placement anchors, the compact table, and the post-window update note. No files will be changed.
exec
/bin/zsh -lc 'git status --short --branch && rg -n "''^(#|##|###)|ACTIVE_STOP_CARD|Current Project Status|Known Workspace State|What Is Next" RUN_STATE.md TASK_QUEUE.md docs/agent_playbook.md docs/process_traces/2026-08-07-meta-sweeps/REFUSAL-CENSUS.md docs/paper/draft-v1.md' in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
## main...origin/main
 M CLAIMS_STATUS.md
 M PROJECT_STATUS.md
 M README.md
 M WINDOW_STATUS.md
 M docs/decision_log.md
docs/paper/draft-v1.md:1:# JouleWise: Attribution-Limited Detection Floors for Phase-Resolved LLM Inference Energy on Apple Silicon
docs/paper/draft-v1.md:5:## Abstract
docs/paper/draft-v1.md:9:## 1. Introduction
docs/paper/draft-v1.md:28:## 2. Background and the gap
docs/paper/draft-v1.md:38:## 3. In-window calibration method
docs/paper/draft-v1.md:40:### Measurement model and boundary
docs/paper/draft-v1.md:48:### Bracketed pulse-train calibration
docs/paper/draft-v1.md:60:## 4. Detection-floor composition
docs/paper/draft-v1.md:64:### Repeatability and false-comparison guards
docs/paper/draft-v1.md:90:### Worst-case timing attribution
docs/paper/draft-v1.md:96:### Measured, never-zero drift allowance
docs/paper/draft-v1.md:115:### Publication label and the two claim gates
docs/paper/draft-v1.md:127:## 5. Fail-closed collection protocol
docs/paper/draft-v1.md:131:### Pre-registration and admission
docs/paper/draft-v1.md:139:### Counterbalanced order
docs/paper/draft-v1.md:143:### Evidence custody and refusals
docs/paper/draft-v1.md:153:## 6. Instrument characterization
docs/paper/draft-v1.md:174:## 7. Demonstration results
docs/paper/draft-v1.md:178:### Pre-registered design
docs/paper/draft-v1.md:182:### Prospective workload sizing
docs/paper/draft-v1.md:188:### Results
docs/paper/draft-v1.md:210:## 8. Discussion
docs/paper/draft-v1.md:218:## 9. Related work
docs/paper/draft-v1.md:220:### LLM inference energy measurement
docs/paper/draft-v1.md:228:### Software power counters and measurement standards
docs/paper/draft-v1.md:234:### Metrology and experimental discipline
docs/paper/draft-v1.md:240:### Split and disaggregated inference
docs/paper/draft-v1.md:246:## 10. Limitations
docs/paper/draft-v1.md:260:## 11. Artifact availability
docs/paper/draft-v1.md:266:## 12. Conclusion
docs/paper/draft-v1.md:272:## 13. References
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
RUN_STATE.md:1:# JouleWise Run State
RUN_STATE.md:16:## ⏳ 2026-08-07 — paper-first session (LIVE; block 3 — near-final state)
RUN_STATE.md:69:## ✅ CHECKPOINT 2026-08-06 late — machine-move stop (resume script)
RUN_STATE.md:123:## ⏳ 2026-08-06 AFTERNOON — re-mint fork: historical consumption is closed at main; Ed's ruling owed
RUN_STATE.md:178:## ✅ CHECKPOINT 2026-08-06 morning — executed by the afternoon session above
RUN_STATE.md:224:#104 registration batch, #106 ledger-bootstrap infra, #107 QUIET-GUARD
RUN_STATE.md:264:## ⏳ 2026-08-05 LATE NIGHT — Fable resume: all 4 audits harvested, D-115 adjudicated, two Sol rounds in flight
RUN_STATE.md:321:### Overnight progress ledger (updated ~23:50; all evidence in .desk + session scratchpad, custody commits as noted)
RUN_STATE.md:364:### D-079 ISSUANCE HELD by cold gate (recorded ~03:30 2026-08-06) — issuance is IMPLEMENTATION, not an edit
RUN_STATE.md:391:### GOVERNING PRIORITY STACK (Ed, 2026-08-06) — all work serves the paper
RUN_STATE.md:400:### SYLLABUS ANCHOR (Ed, 2026-08-06) — the overarching goal
RUN_STATE.md:410:### QG census — magistrate stop-condition set (recorded ~02:40 2026-08-06)
RUN_STATE.md:429:### ESCALATION TRIGGER FIRED — quiet-guard observation-failure→absence class (recorded ~01:15 2026-08-06)
RUN_STATE.md:445:### Ed directive batch (2026-08-05 ~22:00, in-thread; 12-hour autonomous window)
RUN_STATE.md:467:## ✅ CHECKPOINT 2026-08-05 night — Ed model-switch stop (successor is FABLE; read this, then the EVENING queue)
RUN_STATE.md:475:### What landed this session (pushed; main green at `b55008f`)
RUN_STATE.md:494:### IN FLIGHT at checkpoint — harvest, do NOT re-run blind
RUN_STATE.md:526:### Next substantive item (un-gated payoff)
RUN_STATE.md:534:### Standing facts unchanged
RUN_STATE.md:540:## ✅ CHECKPOINT 2026-08-05 evening — DESCOPE + RESUME SCRIPT (still-valid queue; NIGHT block above updates it)
RUN_STATE.md:553:### SUCCESSOR'S QUEUE — start here, all agent-startable desk work
RUN_STATE.md:570:### What landed this session (all pushed; main green)
RUN_STATE.md:587:### IN FLIGHT at checkpoint (harvest from disk — do NOT re-run blind)
RUN_STATE.md:601:### DESCOPE — what is SHELVED (do not build; reopen only on Ed's word)
RUN_STATE.md:613:### Design record worth keeping (from the credential consult, before descope)
RUN_STATE.md:627:### Follow-on rows to register (queued this checkpoint)
RUN_STATE.md:643:### Standing operating facts (unchanged, still binding)
RUN_STATE.md:660:## ✅ 2026-08-05 — Ed's decision batch executed (PR #100 merged; acks recorded; quiet-guard ruled)
RUN_STATE.md:703:## ✅ CHECKPOINT 2026-08-04 ~06:30 — Ed-ordered stop (successor script)
RUN_STATE.md:748:## ✅ CHECKPOINT 2026-08-04 early AM — T3 HANDOFF (successor script)
RUN_STATE.md:761:### What landed overnight (all pushed; nothing dangling)
RUN_STATE.md:867:### ED OWES (nothing blocks the successor's queue)
RUN_STATE.md:887:### Standing operating facts for the successor
RUN_STATE.md:906:## ✅ CHECKPOINT 2026-08-03 late night — T3 CUTOVER (successor session, ACTIVE)
RUN_STATE.md:1043:## ✅ CHECKPOINT 2026-08-03 night — 16h-runway stream state (successor is FABLE, MAGISTRATE, on T3 Code)
RUN_STATE.md:1151:## DESK-SESSION UPDATE (HISTORICAL — superseded by the checkpoint block at top) (2026-08-03, Ed away — first the cold-gate arc, then a sleep-window of non-claim rows) — read this, then the two ⏸️ blocks above
RUN_STATE.md:1243:## EXECUTED RESUME SCRIPT (2026-08-02 ~16:10 PT checkpoint — FULLY EXECUTED by the 2026-08-03 desk session; see the DESK-SESSION UPDATE above; retained as historical record)
RUN_STATE.md:1372:## PRIOR RESUME SCRIPT (2026-08-01 desk session, second checkpoint; resume EXACTLY here)
RUN_STATE.md:1473:## PRIOR ACTIVE RESUME SCRIPT (2026-08-01 ~07:00 PT checkpoint; EXECUTED this desk session — retained for the collection facts)
RUN_STATE.md:1581:## PRIOR ACTIVE RESUME SCRIPT (2026-07-31 ~22:15 PT checkpoint; EXECUTED — window A verdict emitted [FAILED], window B run and salvage-closed; retained for the collection facts)
RUN_STATE.md:1685:## PRIOR STATE (2026-07-31 claims-desk close-out; resume script below FULLY EXECUTED)
RUN_STATE.md:1777:## EXECUTED RESUME SCRIPT (2026-07-30 19:15 PT pre-window checkpoint; historical — fully executed, see CURRENT STATE)
RUN_STATE.md:1856:## PRIOR STATE (2026-07-30 afternoon; the resume script below is EXECUTED except where struck)
RUN_STATE.md:1878:## EXECUTED RESUME SCRIPT (2026-07-30 ~11:00 PT handoff checkpoint; historical)
RUN_STATE.md:2006:## Start Here For Every Big Run
RUN_STATE.md:2026:12. If an `ACTIVE_STOP_CARD` exists below, it overrides every normal
RUN_STATE.md:2055:## Historical Stop-Card Note
RUN_STATE.md:2061:## ACTIVE_STOP_CARD
RUN_STATE.md:2065:## Active Global Work-Selection Gates
RUN_STATE.md:2069:## Restart By Machine-State Lane
RUN_STATE.md:2073:### [ED-EXTERNAL]
RUN_STATE.md:2077:### [QUIET-MAC]
RUN_STATE.md:2081:### [AGENT]
RUN_STATE.md:2087:## CHECKPOINT 2026-07-18 (late): D-077 adversarial arc complete, PR #77 open
RUN_STATE.md:2111:## CHECKPOINT 2026-07-18: Claude script bridge runs in the pet's app task
RUN_STATE.md:2137:## CHECKPOINT 2026-07-17 (late session): env-guard branch open, review pending
RUN_STATE.md:2188:## Superseded stop card (CP-5)
RUN_STATE.md:2200:## Current Project Status
RUN_STATE.md:2207:### The central measurement fact (read before any measurement decision)
RUN_STATE.md:2219:### Collection state
RUN_STATE.md:2259:### The critical path: build the mint (HISTORICAL — CLOSED 2026-07-30)
RUN_STATE.md:2294:### Disk
RUN_STATE.md:2318:### Orchestration
RUN_STATE.md:2326:### What needs Ed
RUN_STATE.md:2382:#59 integration-review fixes and the #60 DOC-008 kernel refresh); none
RUN_STATE.md:2405:## Session History (pointers only — run reports own the narrative)
RUN_STATE.md:2527:## Current Verification
RUN_STATE.md:2628:### Historical verification archive (exact at the recorded heads)
RUN_STATE.md:2774:## Known Workspace State
RUN_STATE.md:2841:## Historical Next-Work Snapshot (superseded 2026-07-15)
RUN_STATE.md:2859:## Reference Decisions And Blockers (non-selection context)
docs/process_traces/2026-08-07-meta-sweeps/REFUSAL-CENSUS.md:18:/bin/zsh -lc 'pwd && git status --short --branch && rg -n "ACTIVE_STOP_CARD|Current Project Status|Known Workspace State|What Is Next" RUN_STATE.md && rg -n "Current Queue|Do-Not-Do-Yet|Do Not Do Yet" TASK_QUEUE.md && rg -n "Mission M0|M0" docs/agent_playbook.md' in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
docs/process_traces/2026-08-07-meta-sweeps/REFUSAL-CENSUS.md:21:## main...origin/main
docs/process_traces/2026-08-07-meta-sweeps/REFUSAL-CENSUS.md:22:2008:12. If an `ACTIVE_STOP_CARD` exists below, it overrides every normal
docs/process_traces/2026-08-07-meta-sweeps/REFUSAL-CENSUS.md:23:2043:## ACTIVE_STOP_CARD
docs/process_traces/2026-08-07-meta-sweeps/REFUSAL-CENSUS.md:24:2182:## Current Project Status
docs/process_traces/2026-08-07-meta-sweeps/REFUSAL-CENSUS.md:25:2743:## Known Workspace State
docs/process_traces/2026-08-07-meta-sweeps/REFUSAL-CENSUS.md:46:12. If an `ACTIVE_STOP_CARD` exists below, it overrides every normal
docs/process_traces/2026-08-07-meta-sweeps/REFUSAL-CENSUS.md:75:## Historical Stop-Card Note
docs/process_traces/2026-08-07-meta-sweeps/REFUSAL-CENSUS.md:81:## ACTIVE_STOP_CARD
docs/process_traces/2026-08-07-meta-sweeps/REFUSAL-CENSUS.md:85:## Active Global Work-Selection Gates
docs/process_traces/2026-08-07-meta-sweeps/REFUSAL-CENSUS.md:89:## Restart By Machine-State Lane
docs/process_traces/2026-08-07-meta-sweeps/REFUSAL-CENSUS.md:93:### [ED-EXTERNAL]
docs/process_traces/2026-08-07-meta-sweeps/REFUSAL-CENSUS.md:97:### [QUIET-MAC]
docs/process_traces/2026-08-07-meta-sweeps/REFUSAL-CENSUS.md:101:### [AGENT]
docs/process_traces/2026-08-07-meta-sweeps/REFUSAL-CENSUS.md:107:## Current Project Status
docs/process_traces/2026-08-07-meta-sweeps/REFUSAL-CENSUS.md:114:### The central measurement fact (read before any measurement decision)
docs/process_traces/2026-08-07-meta-sweeps/REFUSAL-CENSUS.md:126:### Collection state
docs/process_traces/2026-08-07-meta-sweeps/REFUSAL-CENSUS.md:154:## Known Workspace State
docs/process_traces/2026-08-07-meta-sweeps/REFUSAL-CENSUS.md:202:## Current Do-Not-Do-Yet List
docs/process_traces/2026-08-07-meta-sweeps/REFUSAL-CENSUS.md:230:## Queue Maintenance
docs/process_traces/2026-08-07-meta-sweeps/REFUSAL-CENSUS.md:243:## Intake Batch Owed To The Kernel (2026-07-30/31)
docs/process_traces/2026-08-07-meta-sweeps/REFUSAL-CENSUS.md:250:## Current Queue
docs/process_traces/2026-08-07-meta-sweeps/REFUSAL-CENSUS.md:328:## Active Global Work-Selection Gates
docs/process_traces/2026-08-07-meta-sweeps/REFUSAL-CENSUS.md:332:### [ED-EXTERNAL] lane
docs/process_traces/2026-08-07-meta-sweeps/REFUSAL-CENSUS.md:339:# Agent Playbook: Ordered Missions
docs/process_traces/2026-08-07-meta-sweeps/REFUSAL-CENSUS.md:362:## How To Pick A Mission
docs/process_traces/2026-08-07-meta-sweeps/REFUSAL-CENSUS.md:388:## Mission M0: Preflight (every session)
docs/process_traces/2026-08-07-meta-sweeps/REFUSAL-CENSUS.md:390:1. Read only the targeted `RUN_STATE.md` sections: `ACTIVE_STOP_CARD`
docs/process_traces/2026-08-07-meta-sweeps/REFUSAL-CENSUS.md:391:   if present, "Current Project Status", "Known Workspace State", and
docs/process_traces/2026-08-07-meta-sweeps/REFUSAL-CENSUS.md:392:   "What Is Next". If the stop card is ACTIVE, it overrides this
docs/process_traces/2026-08-07-meta-sweeps/REFUSAL-CENSUS.md:429:## Mission M1: Slice 2N — Pre-Hardware Hardening (queue P2-007)
docs/process_traces/2026-08-07-meta-sweeps/REFUSAL-CENSUS.md:459:### 2N.1 `RunContext` seam + raw evidence
docs/process_traces/2026-08-07-meta-sweeps/REFUSAL-CENSUS.md:1747:./docs/reviews/c027/final-examiner.md:17:- **B3 CONFIRMED with a characterization caveat.** RUN_STATE.md:199+ ("What Is Next") orders Wave-2 ranks 0a-0d; TASK_QUEUE.md:96 marks 0a DONE 2026-07-09. Dual-block blocker stands. But the synthesis calls :91-96 "correct" — that block (RUN_STATE.md:94-97) still names P2-022/P2-023 as the next [AGENT] work with only a parenthetical "post-2M sequencing — revisit after Window A" hedge; META blocker #1 flagged exactly this against D-041 (decision_log.md:2050). "Correct" overclaims; "hedged but still ambiguous" is accurate. See §5.
docs/process_traces/2026-08-07-meta-sweeps/REFUSAL-CENSUS.md:2932:# Refusal-scope specification v1 (the ONE home for reason-code scoping)
docs/process_traces/2026-08-07-meta-sweeps/REFUSAL-CENSUS.md:2943:## S1 — Closed scope table
docs/process_traces/2026-08-07-meta-sweeps/REFUSAL-CENSUS.md:2971:## S2 — Normative fail-global defaults
docs/process_traces/2026-08-07-meta-sweeps/REFUSAL-CENSUS.md:2978:## S3 — Named owners of the D-078 gate-1 guarantee
docs/process_traces/2026-08-07-meta-sweeps/REFUSAL-CENSUS.md:2993:## S4 — Change control
docs/process_traces/2026-08-07-meta-sweeps/REFUSAL-CENSUS.md:2999:## Record
docs/process_traces/2026-08-07-meta-sweeps/REFUSAL-CENSUS.md:9701:## main...origin/main
docs/process_traces/2026-08-07-meta-sweeps/REFUSAL-CENSUS.md:9702:## impl/paper-mvp-complete...origin/impl/paper-mvp-complete [ahead 2]
docs/process_traces/2026-08-07-meta-sweeps/REFUSAL-CENSUS.md:9787:# Refusal-mechanism census
docs/process_traces/2026-08-07-meta-sweeps/REFUSAL-CENSUS.md:9791:## 1. Verdict census
docs/process_traces/2026-08-07-meta-sweeps/REFUSAL-CENSUS.md:9805:## 2. Honest denominators
docs/process_traces/2026-08-07-meta-sweeps/REFUSAL-CENSUS.md:9836:## 3. Distinct refusal mechanisms
docs/process_traces/2026-08-07-meta-sweeps/REFUSAL-CENSUS.md:9865:## 4. `{member_id → reason}` reconstructability
docs/process_traces/2026-08-07-meta-sweeps/REFUSAL-CENSUS.md:9883:## 5. Paper-ready table: “The refusal record to date”
docs/process_traces/2026-08-07-meta-sweeps/REFUSAL-CENSUS.md:9899:## Reproduction commands
docs/process_traces/2026-08-07-meta-sweeps/REFUSAL-CENSUS.md:10013:# Refusal-mechanism census
docs/process_traces/2026-08-07-meta-sweeps/REFUSAL-CENSUS.md:10017:## 1. Verdict census
docs/process_traces/2026-08-07-meta-sweeps/REFUSAL-CENSUS.md:10031:## 2. Honest denominators
docs/process_traces/2026-08-07-meta-sweeps/REFUSAL-CENSUS.md:10062:## 3. Distinct refusal mechanisms
docs/process_traces/2026-08-07-meta-sweeps/REFUSAL-CENSUS.md:10091:## 4. `{member_id → reason}` reconstructability
docs/process_traces/2026-08-07-meta-sweeps/REFUSAL-CENSUS.md:10109:## 5. Paper-ready table: “The refusal record to date”
docs/process_traces/2026-08-07-meta-sweeps/REFUSAL-CENSUS.md:10125:## Reproduction commands

exec
/bin/zsh -lc "sed -n '50,90p' docs/agent_playbook.md; sed -n '2060,2088p;2200,2258p;2774,2840p' RUN_STATE.md; sed -n '213,240p;306,384p' TASK_QUEUE.md; sed -n '120,160p' docs/paper/draft-v1.md; sed -n '9787,9925p' docs/process_traces/2026-08-07-meta-sweeps/REFUSAL-CENSUS.md; sed -n '10013,10135p' docs/process_traces/2026-08-07-meta-sweeps/REFUSAL-CENSUS.md" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
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

## CHECKPOINT 2026-07-18 (late): D-077 adversarial arc complete, PR #77 open

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

**2026-08-07 supersession (D-117):** the historical a10/re-mint and old
C/D plan are retired. Claim authority can now arise only from the
prospective alpha, beta, and gamma windows; the separately named Window C
characterization night remains Ed ruling #1. The table above is retained
unchanged as dated collection history, not present claim authority.

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

\[
\text{practical joint-clearance size}=F_{\mathrm{cell}}+B_{\mathrm{claim}}.
\]

For the measured phase-contrast regime, this practical sizing quantity is several joules. It explains how large an effect will generally need to be to clear both gates together and ensures that neither physical uncertainty term is hidden as an apparent double count. It is not a single summed acceptance threshold, and the decision interval is not compared with the sum. Effects that fail the floor gate are reported as *not resolvable*, not as zero, equal, or evidence of no difference. Effects that pass the floor gate but whose interval does not support direction remain unresolved and receive no directional claim.

## 5. Fail-closed collection protocol

*Fail-closed* means that missing, inconsistent, stale, or contaminated evidence produces a refusal rather than an optimistic default. The collection unit is the measurement window defined in Section 3. Work that does not fit within two to four hours with at least a 20% failure margin is split prospectively into another independently calibrated window.

### Pre-registration and admission

Before quiet time, the operator freezes the run identifiers, membership, stage order, comparison definitions, calibration retry count, acceptance thresholds, extraction specification, code revision, and an initially empty waiver list. Every configuration is validated and dry-run against a fresh collection directory. These choices are made before outcomes are visible. Pre-registration here is executable: the launcher and final verifier check the frozen values rather than relying on a narrative promise.

Prospective sizing is part of that freeze. Before collection, the planned effect, workload, and number of independent bundles or ABBA blocks are compared with the cell floor and the claim-side interval width. If the design has too little expected clearance, the operator must prospectively increase independent evidence, change the workload, or narrow the claim; the choice cannot be made after seeing claim data. A workload change is not merely a sensitivity adjustment. For example, lengthening the prompt changes the population of requests being estimated and therefore changes the estimand itself.

Each stage then passes admission gates immediately before measurement. The approved power supply and power policy must be unchanged; displays must be asleep; the screensaver and low-power mode must be off; thermal pressure must be nominal; and central- and graphics-processor activity must meet the quiet-state criteria. Known background work is allowed to finish before the window, followed by a settling interval, rather than being ignored during analysis. Runtime and telemetry identities, clock anchoring, sample cadence, calibration freshness, and post-run environment observations are also checked. No environment override can produce a claim-bearing member.

### Counterbalanced order

Comparisons use the ABBA blocks defined in Section 4. Conditions A and B are measured in the order A, B, B, A, with ordinary cooldown between members. Averaging the two outer A observations and the two inner B observations cancels a linear time trend within the block to first order. For null-floor calibration, A and B are aliases of the same configuration and payload, so any nonzero block difference is a false comparative effect. For scientific contrasts, the A and B definitions are frozen in advance, and the contrast is computed within each block before blocks are aggregated. ABBA reduces common drift; it does not replace the measured whole-window drift allowance.

### Evidence custody and refusals

The bundle defined in Section 3 is the basic custody object. Cryptographic hashes bind the claim-bearing files of each bundle to the campaign record; the binding covers the files the analysis consumes, and the final verdict then fixes the exact member set, so substituting or omitting evidence after collection is detectable. Failed or interrupted artifacts are never deleted or overwritten. Each preserved attempt to collect a declared member is a *recorded occurrence*. Moving an occupied retry slot to quarantine outside the active collection directory is an operator action that the recording tools validate rather than an automatic one; the member is recollected only under an allowed retry; and an append-only supersession record states which recorded occurrence governs. Two present bundles claiming to be the same recorded occurrence cause a refusal. The final whole-window verdict binds the complete declared member set, its preserved attempts and supersessions, the calibration bracket, policy, and drift evidence by hash, so a later consumer cannot silently select a more favorable subset.

Collection does not continue indefinitely through environmental interruptions. Each stage attempt stops at its first member failure, and after the same cause fails a window stage for the third time the window itself closes rather than being retried. In actual operation, nights with three environmental member interruptions were closed and preserved as salvage rather than repeatedly retried. The surviving data may remain diagnostic, but it becomes claim-bearing only if the pre-registered verdict and extraction rules accept the complete resulting member set. This abandon-after-three rule limits outcome-dependent retrying and makes the cost of a noisy environment visible.

Custody — the requirement that every claim trace back to tamper-evident evidence — continues after collection. The immutable corpus is backed up before extraction. The extractor re-authenticates member hashes, required files and cross-file consistency, calibration identity, environment admission, complete campaign membership, cooldown evidence, phase metric identity, and the whole-window drift allowance. It excludes or refuses a cell according to the frozen rules; missing uncertainty never becomes zero. The present boundary is narrower than an independently reusable floor file: a claim-bearing floor must be produced by protocol-controlled extraction and consumed by analysis in one controlled session run and verified by the experimenters. A standalone floor or result artifact is not independently sufficient to authorize a claim.

The refusal log is part of the evaluation, not an embarrassment to omit. It records contaminated members, out-of-family calibration, stale drift evidence, unresolved clock anchors, duplicate recorded occurrences, and below-floor effects. In one real end-of-night case, governed re-evaluation refused a window because a member's internal clock alignment could not be resolved. Independent adjudication found that refusal correct. The result remained non-claim-bearing: an example of the fail-closed design working as intended, not a software defect to be bypassed.

## 6. Instrument characterization

The planned instrument characterization will ask whether the complete measurement system behaves predictably when driven by signals whose qualitative answer is known in advance. The workload will serve as a test signal rather than as the scientific finding. Each test will retain the calibration, admission, custody, and floor rules used for the later demonstration. Existing campaign fragments will not be promoted where the governing whole-window verdict did not pass; the table marks every required claim-bearing result as pending.

| Property | Planned characterization method | What a passing result would establish | Claim-bearing result |
|---|---|---|---|
| Linearity | The study will hold the prompt profile fixed and ramp the requested output from 128 to 2048 tokens. It will regress gross request and token-generation energy on the runtime-observed output count and inspect residual structure as well as the fitted slope. | Energy would respond proportionally over the tested dynamic range, and the fitted per-token slope could serve as the known-effect standard for floor probes on this stack. It would not establish linearity outside the tested range or on another stack. | **[PENDING WINDOW C]** |
| Null response across magnitudes | The study will run identical A-equals-B ABBA blocks at short, medium, and long output magnitudes and evaluate the paired differences against zero and the predicted decision envelopes. | The comparison path would not create a directional effect merely because total energy or duration changes, and false contrasts across the tested range would be contained by the error model. A non-significant result alone would remain insufficient; the interval must be interpreted relative to the floor. | **[PENDING WINDOW C]** |
# Refusal-mechanism census

Scope: all top-level `runs_window_*/campaign_log.jsonl` and `runs*/campaign_log.jsonl` in `/Users/edr/code/JouleWise`, deduplicating the overlapping globs. The temporary session worktree contained no run corpora; Git identified this canonical worktree as the same repository. No repository files were changed.

## 1. Verdict census

The sweep covered 33 unique logs and 1,475 JSONL rows.

- The two globs produced 60 raw path matches but only 33 unique files.
- 27 were `runs_window_*` logs: 18 non-`_bound` roots and 9 `_bound` evidence roots.
- 6 were `runs_recal*` logs.
- 154 records were verdict-typed:

  - 138 `campaign_verdict` rows. These encode collection/preflight state, not `passed`/`failed`: 92 `collection.verdict=usable`, 46 `invalid`; all 138 say claim readiness was `not_assessed`.
  - 16 `idle_admission_whole_window_verdict` rows. These are the only literal pass/fail verdicts: **6 PASSED, 10 FAILED**.

The 16 pass/fail rows cover 13 adjudicated window roots because a5 was re-verdict-ed three times and a8 twice. Taking the latest verdict per root gives **6 passed and 7 failed windows**. Five other non-bound `runs_window_*` roots are fragments/probes without a final whole-window verdict.

## 2. Honest denominators

| Denominator | Exact count |
|---|---:|
| Unique logs | 33 |
| Adjudicated window roots | 13 |
| Whole-window verdict rows | 16 |
| All member log rows | 1,314 |
| Skipped/reused rows, not new attempts | 141 |
| Executed member-attempt rows | 1,173 |
| Successful member outcomes | 1,130 |
| Member-status failures | 43 |
| Collection-refused member occurrences | **44** |
| Distinct refused `(root, member_id)` identities | 38 |
| Distinct executed `(root, member_id)` identities | 1,152 |
| Extra executed retry attempts | 21, across 17 identities |
| Supersession records | 7 |
| Superseded attempts represented | **8** |

The difference between 43 status failures and 44 collection refusals is real: one member executed successfully but was then refused by strict validation because the raw idle trace and uncertainty derivations disagreed with stored metadata.

Prechecks have two separate denominators:

- Campaign environment preflight: **138 occurrences**—136 admitted and 2 exceptionally rejected before member 1. All 138 nevertheless carry `preflight.status="pass"`, so `environment_guard.admitted` is the honest field. The two rejections contain three finding-code hits: `display_not_all_asleep` twice and `low_power_mode_enabled` once as unknown.
- Member metric prechecks: 5,441 raw flag appearances, collapsing repeated verdict snapshots to **4,826 unique `(root, member_id, code)` occurrences**:

  - **4,818 metric-local/by-design refusal-mechanism occurrences**, affecting 1,127 members.
  - **8 exceptional global occurrences**, affecting 5 members: `clock_anchor_unresolved` ×3, `environment_admission_missing` ×4, and `environment_admission_failed` ×1.

“By design” means the gate is deliberately metric-local under the [refusal-scope specification](/Users/edr/code/JouleWise/docs/phase_2/refusal_scope_spec.md:1); it does not mean every poor-quality metric was expected or desirable.

## 3. Distinct refusal mechanisms

There are **26 distinct machine-readable reason codes**. Grouping same-cause and downstream aliases yields these 10 mechanism families. Counts use their native denominator and therefore overlap across layers; they must not be summed.

| Grouped mechanism | Exact observed occurrence count | Reason representation |
|---|---:|---|
| Window too short or undersampled | 1,135 member-code pairs across 1,127 members | Codes: `nonpositive_window_duration`, `insufficient_in_window_samples` |
| Cadence evidence absent or inadequate | 1,464 pairs across 1,127 members | Codes: `cadence_ratio_unrecorded`, `cadence_ratio_below_threshold` |
| Clock evidence inadequate | 1,127 metric-local clock-bound pairs, plus 3 exceptional unresolved-clock occurrences | Codes: `clock_bound_unrecorded`, `clock_bound_exceeds_quarter_window`, `clock_anchor_unresolved` |
| Interpolation uncertainty absent | 8 pairs across 8 members | Code: `interpolation_bound_unrecorded` |
| Anchor-envelope/fallback gate | 1,084 precheck pairs across 742 members; 3 collection-refused members | Codes: two `anchor_energy_envelope_*` codes and `anchor_fallback_member_unusable` |
| Environment/admission interference | 2 pre-member campaign refusals; 5 exceptional member-precheck occurrences; 8 superseded contaminated attempts; 6 failed whole-window rows across 4 roots | Machine codes at precheck/verdict layers; the causal supersession explanations are free text |
| Prompt-hash/suite-recording failure | 5 member refusals | Code `prompt_hash_check_error`, with free-text validation details |
| Custody, validation, or membership failure | 9 failed verdict rows across 6 roots; additionally 1 successful execution refused by strict validation | Whole-window codes; the single post-run mismatch is free text only |
| Instrument calibration missing or inconsistent | 3 failed verdict rows across 3 roots: 2 missing brackets and 1 calibration mismatch | Machine-readable codes |
| NEG-8 bracket/drift failure | 8 failed verdict rows across 5 roots, containing 10 reason-code hits | Four codes: bracket missing, reference invalid, drift excessive, and drift stale |

Thirty of the 44 refused member occurrences have **no causal reason at all** in these logs—only failed/invalid status. “Invalid unwaived member bundle” was not counted as a cause because it merely restates the verdict.

Specific §5 claim checks:

- Contaminated/environmentally interrupted attempts: **8**, documented by 7 supersession records.
- Out-of-family calibration: **1** `instrument_calibration_mismatch` verdict.
- Stale drift evidence: **2** failed verdict rows in 2 roots.
- Unresolved clock anchors: **3** member precheck occurrences.
- Active duplicate-occurrence refusal: **0**. The corpus contains 7 successful supersession records covering 8 replaced attempts, but no duplicate refusal.
- Below-floor refusal: **0**. All 138 campaign verdicts leave claim readiness `not_assessed`; no log string matches `below_floor`.
- Neither `duplicate` nor `below_floor` appears anywhere as a string in the swept logs.

## 4. `{member_id → reason}` reconstructability

Member identity must be scoped by root because names recur between campaigns.

- Identity-level rate: **13 / 38 = 34.21052631578947%**.
- Occurrence-level rate: **14 / 44 = 31.818181818181817%**.

Occurrence-level breakdown:

| Reason availability | Refused occurrences |
|---|---:|
| Machine-readable causal code | 8 |
| Validation reason in free text only | 1 |
| Supersession reason in free text only | 5 |
| No causal reason reconstructable | **30** |

Thus the campaign logs prove that refusals happened much more reliably than they explain why each member was refused.

## 5. Paper-ready table: “The refusal record to date”

| Refusal record to date | Observed record |
|---|---|
| Whole-window decisions | Thirteen window roots have final decisions: six passed and seven failed. The append-only logs contain sixteen decision rows because two windows were evaluated more than once; across those rows, six passed and ten failed. |
| Member collection | There were 1,173 executed member attempts. Forty-four occurrences were refused: 43 failed during collection and one completed but failed strict evidence validation. |
| Pre-window admission | Of 138 campaign prechecks, 136 admitted collection and two stopped before the first member because the machine was not in the required state. |
| Environmental interruption | Seven supersession records preserve eight replaced attempts. Their explanations name background CPU activity, display/login disturbance, or an operator wake event. |
| Calibration and drift | One verdict refused an inconsistent instrument calibration; two lacked a calibration bracket. NEG-8 bracket or drift evidence contributed to eight failed verdict rows across five window roots, including two stale-drift verdicts. |
| Clock evidence | Three members carried an unresolved-clock-anchor refusal. Many shorter metric windows were also refused locally because their clock bound was absent or too large for that metric. |
| Duplicate handling | Eight prior attempts were resolved through seven append-only supersession records. No active duplicate-occurrence refusal appears in this corpus. |
| Below-floor effects | No below-floor claim refusal appears: claim readiness was not assessed in all 138 campaign verdict rows. |
| Logging completeness | A causal member-level reason can be reconstructed for only 13 of 38 refused member identities, or 14 of 44 refused occurrences. Thirty refused occurrences retain status but no causal reason. |

This is the defensible replacement for the broad claim currently in [§5](/Users/edr/code/JouleWise/docs/paper/draft-v1.md:143): the record supports contamination, calibration, drift, clock, custody, and supersession behavior, but not yet an observed below-floor or active-duplicate refusal.

## Reproduction commands

Path resolution:

```zsh
setopt null_glob
cd /Users/edr/code/JouleWise
files=(runs_window_*/campaign_log.jsonl runs*/campaign_log.jsonl)
printf '%s\n' "${files[@]}" | sed '/^$/d' | LC_ALL=C sort -u
printf 'RAW_MATCHES=%d\n' ${#files[@]}
printf '%s\n' "${files[@]}" | sed '/^$/d' | LC_ALL=C sort -u | wc -l
```

Member denominators:

```zsh
for f in ${(u)files}; do
  jq -c --arg file "$f" \
    'select(.record_type==null) |
     {file:$file,run_id,status,exit_code,
      member_status:.members[0].status,
      collection_classification:.members[0].collection_classification}' "$f"
done |
jq -s '{
  member_log_rows:length,
  executed_attempt_rows:(map(select(.status!="skipped"))|length),
  skipped_reuse_rows:(map(select(.status=="skipped"))|length),
# Refusal-mechanism census

Scope: all top-level `runs_window_*/campaign_log.jsonl` and `runs*/campaign_log.jsonl` in `/Users/edr/code/JouleWise`, deduplicating the overlapping globs. The temporary session worktree contained no run corpora; Git identified this canonical worktree as the same repository. No repository files were changed.

## 1. Verdict census

The sweep covered 33 unique logs and 1,475 JSONL rows.

- The two globs produced 60 raw path matches but only 33 unique files.
- 27 were `runs_window_*` logs: 18 non-`_bound` roots and 9 `_bound` evidence roots.
- 6 were `runs_recal*` logs.
- 154 records were verdict-typed:

  - 138 `campaign_verdict` rows. These encode collection/preflight state, not `passed`/`failed`: 92 `collection.verdict=usable`, 46 `invalid`; all 138 say claim readiness was `not_assessed`.
  - 16 `idle_admission_whole_window_verdict` rows. These are the only literal pass/fail verdicts: **6 PASSED, 10 FAILED**.

The 16 pass/fail rows cover 13 adjudicated window roots because a5 was re-verdict-ed three times and a8 twice. Taking the latest verdict per root gives **6 passed and 7 failed windows**. Five other non-bound `runs_window_*` roots are fragments/probes without a final whole-window verdict.

## 2. Honest denominators

| Denominator | Exact count |
|---|---:|
| Unique logs | 33 |
| Adjudicated window roots | 13 |
| Whole-window verdict rows | 16 |
| All member log rows | 1,314 |
| Skipped/reused rows, not new attempts | 141 |
| Executed member-attempt rows | 1,173 |
| Successful member outcomes | 1,130 |
| Member-status failures | 43 |
| Collection-refused member occurrences | **44** |
| Distinct refused `(root, member_id)` identities | 38 |
| Distinct executed `(root, member_id)` identities | 1,152 |
| Extra executed retry attempts | 21, across 17 identities |
| Supersession records | 7 |
| Superseded attempts represented | **8** |

The difference between 43 status failures and 44 collection refusals is real: one member executed successfully but was then refused by strict validation because the raw idle trace and uncertainty derivations disagreed with stored metadata.

Prechecks have two separate denominators:

- Campaign environment preflight: **138 occurrences**—136 admitted and 2 exceptionally rejected before member 1. All 138 nevertheless carry `preflight.status="pass"`, so `environment_guard.admitted` is the honest field. The two rejections contain three finding-code hits: `display_not_all_asleep` twice and `low_power_mode_enabled` once as unknown.
- Member metric prechecks: 5,441 raw flag appearances, collapsing repeated verdict snapshots to **4,826 unique `(root, member_id, code)` occurrences**:

  - **4,818 metric-local/by-design refusal-mechanism occurrences**, affecting 1,127 members.
  - **8 exceptional global occurrences**, affecting 5 members: `clock_anchor_unresolved` ×3, `environment_admission_missing` ×4, and `environment_admission_failed` ×1.

“By design” means the gate is deliberately metric-local under the [refusal-scope specification](/Users/edr/code/JouleWise/docs/phase_2/refusal_scope_spec.md:1); it does not mean every poor-quality metric was expected or desirable.

## 3. Distinct refusal mechanisms

There are **26 distinct machine-readable reason codes**. Grouping same-cause and downstream aliases yields these 10 mechanism families. Counts use their native denominator and therefore overlap across layers; they must not be summed.

| Grouped mechanism | Exact observed occurrence count | Reason representation |
|---|---:|---|
| Window too short or undersampled | 1,135 member-code pairs across 1,127 members | Codes: `nonpositive_window_duration`, `insufficient_in_window_samples` |
| Cadence evidence absent or inadequate | 1,464 pairs across 1,127 members | Codes: `cadence_ratio_unrecorded`, `cadence_ratio_below_threshold` |
| Clock evidence inadequate | 1,127 metric-local clock-bound pairs, plus 3 exceptional unresolved-clock occurrences | Codes: `clock_bound_unrecorded`, `clock_bound_exceeds_quarter_window`, `clock_anchor_unresolved` |
| Interpolation uncertainty absent | 8 pairs across 8 members | Code: `interpolation_bound_unrecorded` |
| Anchor-envelope/fallback gate | 1,084 precheck pairs across 742 members; 3 collection-refused members | Codes: two `anchor_energy_envelope_*` codes and `anchor_fallback_member_unusable` |
| Environment/admission interference | 2 pre-member campaign refusals; 5 exceptional member-precheck occurrences; 8 superseded contaminated attempts; 6 failed whole-window rows across 4 roots | Machine codes at precheck/verdict layers; the causal supersession explanations are free text |
| Prompt-hash/suite-recording failure | 5 member refusals | Code `prompt_hash_check_error`, with free-text validation details |
| Custody, validation, or membership failure | 9 failed verdict rows across 6 roots; additionally 1 successful execution refused by strict validation | Whole-window codes; the single post-run mismatch is free text only |
| Instrument calibration missing or inconsistent | 3 failed verdict rows across 3 roots: 2 missing brackets and 1 calibration mismatch | Machine-readable codes |
| NEG-8 bracket/drift failure | 8 failed verdict rows across 5 roots, containing 10 reason-code hits | Four codes: bracket missing, reference invalid, drift excessive, and drift stale |

Thirty of the 44 refused member occurrences have **no causal reason at all** in these logs—only failed/invalid status. “Invalid unwaived member bundle” was not counted as a cause because it merely restates the verdict.

Specific §5 claim checks:

- Contaminated/environmentally interrupted attempts: **8**, documented by 7 supersession records.
- Out-of-family calibration: **1** `instrument_calibration_mismatch` verdict.
- Stale drift evidence: **2** failed verdict rows in 2 roots.
- Unresolved clock anchors: **3** member precheck occurrences.
- Active duplicate-occurrence refusal: **0**. The corpus contains 7 successful supersession records covering 8 replaced attempts, but no duplicate refusal.
- Below-floor refusal: **0**. All 138 campaign verdicts leave claim readiness `not_assessed`; no log string matches `below_floor`.
- Neither `duplicate` nor `below_floor` appears anywhere as a string in the swept logs.

## 4. `{member_id → reason}` reconstructability

Member identity must be scoped by root because names recur between campaigns.

- Identity-level rate: **13 / 38 = 34.21052631578947%**.
- Occurrence-level rate: **14 / 44 = 31.818181818181817%**.

Occurrence-level breakdown:

| Reason availability | Refused occurrences |
|---|---:|
| Machine-readable causal code | 8 |
| Validation reason in free text only | 1 |
| Supersession reason in free text only | 5 |
| No causal reason reconstructable | **30** |

Thus the campaign logs prove that refusals happened much more reliably than they explain why each member was refused.

## 5. Paper-ready table: “The refusal record to date”

| Refusal record to date | Observed record |
|---|---|
| Whole-window decisions | Thirteen window roots have final decisions: six passed and seven failed. The append-only logs contain sixteen decision rows because two windows were evaluated more than once; across those rows, six passed and ten failed. |
| Member collection | There were 1,173 executed member attempts. Forty-four occurrences were refused: 43 failed during collection and one completed but failed strict evidence validation. |
| Pre-window admission | Of 138 campaign prechecks, 136 admitted collection and two stopped before the first member because the machine was not in the required state. |
| Environmental interruption | Seven supersession records preserve eight replaced attempts. Their explanations name background CPU activity, display/login disturbance, or an operator wake event. |
| Calibration and drift | One verdict refused an inconsistent instrument calibration; two lacked a calibration bracket. NEG-8 bracket or drift evidence contributed to eight failed verdict rows across five window roots, including two stale-drift verdicts. |
| Clock evidence | Three members carried an unresolved-clock-anchor refusal. Many shorter metric windows were also refused locally because their clock bound was absent or too large for that metric. |
| Duplicate handling | Eight prior attempts were resolved through seven append-only supersession records. No active duplicate-occurrence refusal appears in this corpus. |
| Below-floor effects | No below-floor claim refusal appears: claim readiness was not assessed in all 138 campaign verdict rows. |
| Logging completeness | A causal member-level reason can be reconstructed for only 13 of 38 refused member identities, or 14 of 44 refused occurrences. Thirty refused occurrences retain status but no causal reason. |

This is the defensible replacement for the broad claim currently in [§5](/Users/edr/code/JouleWise/docs/paper/draft-v1.md:143): the record supports contamination, calibration, drift, clock, custody, and supersession behavior, but not yet an observed below-floor or active-duplicate refusal.

## Reproduction commands

Path resolution:

```zsh
setopt null_glob
cd /Users/edr/code/JouleWise
files=(runs_window_*/campaign_log.jsonl runs*/campaign_log.jsonl)
printf '%s\n' "${files[@]}" | sed '/^$/d' | LC_ALL=C sort -u
printf 'RAW_MATCHES=%d\n' ${#files[@]}
printf '%s\n' "${files[@]}" | sed '/^$/d' | LC_ALL=C sort -u | wc -l

exec
/bin/zsh -lc "nl -ba docs/paper/draft-v1.md | sed -n '127,160p;246,265p'" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
   127	## 5. Fail-closed collection protocol
   128	
   129	*Fail-closed* means that missing, inconsistent, stale, or contaminated evidence produces a refusal rather than an optimistic default. The collection unit is the measurement window defined in Section 3. Work that does not fit within two to four hours with at least a 20% failure margin is split prospectively into another independently calibrated window.
   130	
   131	### Pre-registration and admission
   132	
   133	Before quiet time, the operator freezes the run identifiers, membership, stage order, comparison definitions, calibration retry count, acceptance thresholds, extraction specification, code revision, and an initially empty waiver list. Every configuration is validated and dry-run against a fresh collection directory. These choices are made before outcomes are visible. Pre-registration here is executable: the launcher and final verifier check the frozen values rather than relying on a narrative promise.
   134	
   135	Prospective sizing is part of that freeze. Before collection, the planned effect, workload, and number of independent bundles or ABBA blocks are compared with the cell floor and the claim-side interval width. If the design has too little expected clearance, the operator must prospectively increase independent evidence, change the workload, or narrow the claim; the choice cannot be made after seeing claim data. A workload change is not merely a sensitivity adjustment. For example, lengthening the prompt changes the population of requests being estimated and therefore changes the estimand itself.
   136	
   137	Each stage then passes admission gates immediately before measurement. The approved power supply and power policy must be unchanged; displays must be asleep; the screensaver and low-power mode must be off; thermal pressure must be nominal; and central- and graphics-processor activity must meet the quiet-state criteria. Known background work is allowed to finish before the window, followed by a settling interval, rather than being ignored during analysis. Runtime and telemetry identities, clock anchoring, sample cadence, calibration freshness, and post-run environment observations are also checked. No environment override can produce a claim-bearing member.
   138	
   139	### Counterbalanced order
   140	
   141	Comparisons use the ABBA blocks defined in Section 4. Conditions A and B are measured in the order A, B, B, A, with ordinary cooldown between members. Averaging the two outer A observations and the two inner B observations cancels a linear time trend within the block to first order. For null-floor calibration, A and B are aliases of the same configuration and payload, so any nonzero block difference is a false comparative effect. For scientific contrasts, the A and B definitions are frozen in advance, and the contrast is computed within each block before blocks are aggregated. ABBA reduces common drift; it does not replace the measured whole-window drift allowance.
   142	
   143	### Evidence custody and refusals
   144	
   145	The bundle defined in Section 3 is the basic custody object. Cryptographic hashes bind the claim-bearing files of each bundle to the campaign record; the binding covers the files the analysis consumes, and the final verdict then fixes the exact member set, so substituting or omitting evidence after collection is detectable. Failed or interrupted artifacts are never deleted or overwritten. Each preserved attempt to collect a declared member is a *recorded occurrence*. Moving an occupied retry slot to quarantine outside the active collection directory is an operator action that the recording tools validate rather than an automatic one; the member is recollected only under an allowed retry; and an append-only supersession record states which recorded occurrence governs. Two present bundles claiming to be the same recorded occurrence cause a refusal. The final whole-window verdict binds the complete declared member set, its preserved attempts and supersessions, the calibration bracket, policy, and drift evidence by hash, so a later consumer cannot silently select a more favorable subset.
   146	
   147	Collection does not continue indefinitely through environmental interruptions. Each stage attempt stops at its first member failure, and after the same cause fails a window stage for the third time the window itself closes rather than being retried. In actual operation, nights with three environmental member interruptions were closed and preserved as salvage rather than repeatedly retried. The surviving data may remain diagnostic, but it becomes claim-bearing only if the pre-registered verdict and extraction rules accept the complete resulting member set. This abandon-after-three rule limits outcome-dependent retrying and makes the cost of a noisy environment visible.
   148	
   149	Custody — the requirement that every claim trace back to tamper-evident evidence — continues after collection. The immutable corpus is backed up before extraction. The extractor re-authenticates member hashes, required files and cross-file consistency, calibration identity, environment admission, complete campaign membership, cooldown evidence, phase metric identity, and the whole-window drift allowance. It excludes or refuses a cell according to the frozen rules; missing uncertainty never becomes zero. The present boundary is narrower than an independently reusable floor file: a claim-bearing floor must be produced by protocol-controlled extraction and consumed by analysis in one controlled session run and verified by the experimenters. A standalone floor or result artifact is not independently sufficient to authorize a claim.
   150	
   151	The refusal log is part of the evaluation, not an embarrassment to omit. It records contaminated members, out-of-family calibration, stale drift evidence, unresolved clock anchors, duplicate recorded occurrences, and below-floor effects. In one real end-of-night case, governed re-evaluation refused a window because a member's internal clock alignment could not be resolved. Independent adjudication found that refusal correct. The result remained non-claim-bearing: an example of the fail-closed design working as intended, not a software defect to be bypassed.
   152	
   153	## 6. Instrument characterization
   154	
   155	The planned instrument characterization will ask whether the complete measurement system behaves predictably when driven by signals whose qualitative answer is known in advance. The workload will serve as a test signal rather than as the scientific finding. Each test will retain the calibration, admission, custody, and floor rules used for the later demonstration. Existing campaign fragments will not be promoted where the governing whole-window verdict did not pass; the table marks every required claim-bearing result as pending.
   156	
   157	| Property | Planned characterization method | What a passing result would establish | Claim-bearing result |
   158	|---|---|---|---|
   159	| Linearity | The study will hold the prompt profile fixed and ramp the requested output from 128 to 2048 tokens. It will regress gross request and token-generation energy on the runtime-observed output count and inspect residual structure as well as the fitted slope. | Energy would respond proportionally over the tested dynamic range, and the fitted per-token slope could serve as the known-effect standard for floor probes on this stack. It would not establish linearity outside the tested range or on another stack. | **[PENDING WINDOW C]** |
   160	| Null response across magnitudes | The study will run identical A-equals-B ABBA blocks at short, medium, and long output magnitudes and evaluate the paired differences against zero and the predicted decision envelopes. | The comparison path would not create a directional effect merely because total energy or duration changes, and false contrasts across the tested range would be contained by the error model. A non-significant result alone would remain insufficient; the interval must be interpreted relative to the floor. | **[PENDING WINDOW C]** |
   246	## 10. Limitations
   247	
   248	**Attribution-limited resolution.** The dominant uncertainty on the studied implementation is boundary placement, not scatter. Roughly one joule per phase member can be misassigned when calibrated timing uncertainty of tens of milliseconds meets a power swing of tens of watts, and repetitions do not reduce it. When attribution dominance is the sole otherwise-refusing condition and an exact corner-widened floor exists, the result may be published with an explicit attribution-limited label; that label never rescues any other refusal. The floor plus claim-side bound remains a practical several-joule sizing disclosure, not one summed acceptance threshold. A historical non-claim diagnostic of the short-prompt model-size contrast had a point estimate marginally above that practical bar, but its composed interval overlapped the bar. That diagnostic motivated the prospective floors-only prompt-processing default in Section 7; it was not a fresh measurement or an issued refusal. The resulting limitation concerns what this implementation, on the named stack and boundary, can support.
   249	
   250	**One unit, one stack, one boundary.** Every result is scoped to one physical machine, operating-system build, runtime and library stack, model artifact, quantization, tokenizer, sampling and output policy, telemetry backend, and measurement boundary. Nothing here ranks hardware classes or vendors, and the whole-system-on-chip boundary of *powermetrics* is not comparable to a graphics-board or wall boundary without a calibrated bridge.
   251	
   252	**No external meter.** The calibration validates timing attribution—whether samples near a commanded edge land inside or outside a phase integral. It does not validate the counter's absolute gain or whole-system scale; absolute joule values remain internal to the named software boundary. A wall-power instrument could test totals but would still not adjudicate the division of a total between phases, which is the question the pulse-train experiment answers.
   253	
   254	**Transfer assumptions.** The calibration pulses are graphics-processor matrix multiplications under light central-processor load; transferring their timing bound to sustained mixed-load inference is an explicit assumption, constrained by the in-window bracket and the planned empirical floor probes but not eliminated. The drift allowance is measured per window with no duration-scaling law because the evidence does not identify one; longer windows than those characterized would need fresh drift evidence.
   255	
   256	**Sequential requests only.** Phase boundaries are well posed because one request runs at a time. Continuous batching, speculative decoding, and multi-request serving overlap phases by design and are out of scope; the method would need a defensible boundary definition before it could be extended there.
   257	
   258	**Operational constraints as evidence.** Claim-bearing windows require a machine quiescent to the admission gates—no interactive agent sessions, displays asleep, and background work settled. Characterization captures of the idle environment, kept permanently non-claim-bearing, show a low but bursty floor whose excursions, not its mean, threaten a several-joule practical clearance size; idle subtraction cancels only the steady part. The zero-agent window rule is therefore load-bearing, and results collected outside it would not be admitted.
   259	
   260	## 11. Artifact availability
   261	
   262	JouleWise is an open tool. The current repository contains the runner, calibration and reduction code, admission gates, verdict and extraction tooling, and protocol records. The claim-bearing characterization and demonstration evidence will become available only after the corrected artifacts pass the release checklist and their repository and archive locators are published. **[REPOSITORY AND ARCHIVE LOCATORS PENDING RELEASE CHECKLIST]**
   263	
   264	The present custody boundary must be kept with those artifacts. A standalone floor or result artifact is not independently sufficient to authorize a claim. Claim-bearing floors are produced by protocol-controlled extraction and consumed by the analysis in one controlled session run and verified by the experimenters. Within that session, cryptographic hashes bind raw power traces, runtime events, configurations, calibration brackets, drift references, supersession records, and the whole-window verdict. Once the archive is released, a reader will be able to reduce the published results again and verify that the complete member set bound by the verdict is the set consumed by the claims. Superseded artifacts will remain available with their supersession records rather than being deleted.
   265	

exec
/bin/zsh -lc "nl -ba docs/paper/draft-v1.md | sed -n '174,218p'; rg -n \"alpha|beta|gamma|three prospective|prospective windows\" docs/paper/draft-v1.md" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 exited 1 in 0ms:
   174	## 7. Demonstration results
   175	
   176	The planned demonstration will ask a deliberately modest scientific question: on one named consumer stack, how does phase-resolved energy per request differ between two sizes of the same model family, and can each registered difference pass its own floor and direction gates? The two conditions will be instruction-tuned models of the same family at roughly 1.5 and 7 billion parameters, both 4-bit quantized, served by the same runtime with an identical prompt and fixed output budget. Demonstration measurements will be collected in dedicated quiet windows under Section 5, with the floors of Section 4 derived from the protocol-controlled floor windows.
   177	
   178	### Pre-registered design
   179	
   180	Each model size will receive its own floor cell per phase: an absolute-repeatability arm and a null ABBA arm, both frozen before collection. The adopted pre-registered default keeps prompt-processing floor cells in both model-specific floor windows but registers the model-size directional contrast for token generation only. The contrast will be computed within ABBA blocks whose A and B are the two model sizes, on the frozen phase-energy metric. Its floor gate will compare the point-estimate magnitude with the cell floor; its separate direction gate will ask whether both endpoints of the composed interval support the registered direction.
   181	
   182	### Prospective workload sizing
   183	
   184	A non-claim diagnostic analysis of earlier captures informed that default. For the natural short prompt, the prompt-processing model-size contrast had a point estimate marginally above the practical joint-clearance bar, while its composed uncertainty interval overlapped the bar. This was a prospective design warning, not an issued refusal: no fresh demonstration contrast has been measured or refused. The token-generation contrast showed substantially more prospective clearance.
   185	
   186	One declared alternative remains under consideration and would replace the default only through an operator decision frozen before collection: a longer prompt projected to put the prompt-processing contrast at roughly twice the practical bar. That projection is an extrapolation from prompt-length scaling observed on the smaller model; no long-prompt evidence exists for the larger model, so the fresh arm would be its first direct test. Lengthening the prompt would also change the estimand, as Section 5 explains. All results in this section are reported under the adopted default unless that replacement is frozen first.
   187	
   188	### Results
   189	
   190	**[RESULT PENDING CORRECTED ARTIFACTS — tables below are structural placeholders; no energy value from superseded artifacts is carried into this draft.]**
   191	
   192	Table 1. Phase results on the studied stack. The caption accompanying populated results will state the common physical unit, operating system, runtime and libraries, model artifact and quantization, tokenizer, sampler and output policy, concurrency policy, telemetry backend, and measurement boundary. Each interval will be the fully composed two-sided measurement interval; \(n\) counts independent valid run bundles, not samples or items within a bundle.
   193	
   194	| Phase | Model | Gross J/request (lower, upper) | J per prompt token | J per output token | Cell floor (labelled) | n |
   195	|---|---|---|---|---|---|---|
   196	| prompt processing | 1.5B | [PENDING] | [PENDING] | — | [PENDING] | [PENDING] |
   197	| prompt processing | 7B | [PENDING] | [PENDING] | — | [PENDING] | [PENDING] |
   198	| token generation | 1.5B | [PENDING] | — | [PENDING] | [PENDING] | [PENDING] |
   199	| token generation | 7B | [PENDING] | — | [PENDING] | [PENDING] | [PENDING] |
   200	
   201	Table 2. The pre-registered contrast and the declared floors-only phase on the same stack. A registered contrast will aggregate independent ABBA blocks. The floor gate compares the point-estimate magnitude with the cell floor; the direction gate checks whether both endpoints of the fully composed interval support the registered direction. The claim-side bound is shown separately. The two gates are not replaced by a summed threshold.
   202	
   203	| Contrast | Point estimate | Interval [lower, upper] | Cell floor | Clearance (point − floor) | Claim-side bound | Floor-gate outcome | Direction-gate outcome | Verdict |
   204	|---|---|---|---|---|---|---|---|---|
   205	| token generation, 7B − 1.5B | [PENDING] | [PENDING, PENDING] | [PENDING] | [PENDING] | [PENDING] | [PENDING] | [PENDING] | [PENDING] |
   206	| prompt processing, 7B − 1.5B | not registered under the adopted default | not registered | [PENDING] | not applicable | not applicable | not evaluated | not evaluated | floors only |
   207	
   208	The narrative will state, for each registered contrast, whether both gates passed and will quote the refusal log where the protocol declined evidence. Joules per token are tokenizer-scoped companion metrics; they will not be compared across tokenizers. A quantization ladder will be included only if it is collected under its own stack-specific floors within the frozen window budget.
   209	
   210	## 8. Discussion
   211	
   212	The dominant limitation is attribution rather than scatter. Repeating a workload can narrow random variation, but it cannot determine which phase owns energy near a boundary when the counter's timing and the runtime clock do not align exactly. For studies built on software power counters, this changes the experimental priority: collecting more repetitions is useful only after boundary timing, sampling behavior, and drift are bounded. Otherwise, a precise mean can conceal a systematic phase-assignment error.
   213	
   214	A published refusal is scientifically useful because it maps the operating domain of the measurement method. A contaminated window, an unresolved clock anchor, or a contrast that fails a gate is not evidence that two systems are equal. It is evidence that the named implementation cannot support that claim under the recorded conditions. Preserving the failed evidence and its reason prevents selective reporting and helps later work distinguish a small physical effect from an inadequate measurement.
   215	
   216	Prompt length illustrates why feasibility is tied to the estimand. A longer prompt can increase prompt-processing energy and make a contrast easier to resolve, but it answers a different question about a different request population. Feasibility therefore means that a pre-registered design can adjudicate the effect it actually names, not that the workload can be enlarged until any difference becomes visible. Beyond this Apple-silicon stack, the transferable contribution is the method—calibrate boundary attribution, measure drift, separate floor and direction gates, and preserve refusals—not the numerical floor, which must be established again for each instrument, boundary, and stack.
   217	
   218	## 9. Related work

codex
## Placement

In §5, replace the paragraph beginning:

> “The refusal log is part of the evaluation, not an embarrassment to omit.”

and ending:

> “...not a software defect to be bypassed.”

with the following:

The refusal record is part of the evaluation, but the instrument’s development history also tests the completeness of that record. The verified census covers 33 unique campaign logs containing 1,475 entries. These counts describe the instrument’s development history; they are not results from the three prospective windows.

*Table [NUMBER PENDING]. The refusal record to date during instrument development. Mechanism counts overlap and must not be summed.*

| Record | Verified development history |
|---|---|
| Whole-window decisions | 13 window roots: 6 passed and 7 failed. The append-only logs contain 16 decision rows—6 passed and 10 failed—because two windows were evaluated more than once. |
| Member collection | 1,173 executed attempts; 44 refused occurrences: 43 failed during collection and 1 completed but was refused by strict evidence validation. |
| Pre-window admission | 138 campaign prechecks: 136 admitted collection and 2 stopped before the first member. |
| Environment and supersession | 7 supersession records preserve 8 replaced attempts after background processor activity, display or login disturbance, or an operator wake event. |
| Calibration and drift | 1 inconsistent calibration and 2 missing calibration brackets. Bracket or drift evidence contributed to 8 failed decision rows across 5 roots, including 2 stale-drift verdicts. |
| Clock and validation | 3 unresolved clock-anchor occurrences. Custody, validation, or membership failures contributed to 9 failed decision rows across 6 roots. |
| Not observed | 0 active duplicate-occurrence refusals and 0 below-floor claim refusals; all 138 campaign verdicts left claim readiness unassessed. |
| Causal-reason coverage | Occurrences: 14 of 44 (31.8%). Distinct member identities: 13 of 38 (34.2%). Thirty refused occurrences retain no reconstructable cause. |

The record therefore proves that refusals happened far more reliably than it explains why each member was refused. Of the 44 refused occurrences, 14 have a reconstructable cause: 8 from machine-readable codes and 6 only from free text—1 validation explanation and 5 supersession explanations. The remaining 30 preserve a failed or invalid status but no causal explanation. This is a limitation of the development record, not a reason to omit it, and it motivates recording a structured causal reason at the point of every refusal.

The two completeness rates answer different questions. Occurrence-level accounting treats each refused attempt separately, yielding 14 of 44 (31.8%). Identity-level accounting collapses repeated attempts for the same member within a campaign, yielding 13 of 38 (34.2%). These denominators are different, and neither result is derived from the other.

One reconstructable case remains illustrative: an end-of-night re-evaluation refused a window because one member’s internal clock alignment could not be resolved. Independent adjudication upheld the refusal, and the result remained non-claim-bearing. The three prospective windows will add their own admissions, attempts, refusals, supersessions, whole-window decisions, and causal-reason coverage to this record. **[PENDING THREE PROSPECTIVE WINDOWS]**

## After the three windows

Update the bracketed marker only after all three windows have final verdicts and their logs have been audited. Then:

- Preserve the development-history counts as the dated baseline; report the prospective additions and combined totals separately.
- Recount window roots and decision rows independently, since retries may create more decision rows than roots.
- Add the new admission, attempt, refusal, supersession, calibration, drift, clock, validation, duplicate, and below-floor counts.
- Recalculate occurrence-level and identity-level reason coverage independently, retaining both fractions and percentages.
- Renumber this table and the existing results tables.

No files were changed.
tokens used
43,022
## Placement

In §5, replace the paragraph beginning:

> “The refusal log is part of the evaluation, not an embarrassment to omit.”

and ending:

> “...not a software defect to be bypassed.”

with the following:

The refusal record is part of the evaluation, but the instrument’s development history also tests the completeness of that record. The verified census covers 33 unique campaign logs containing 1,475 entries. These counts describe the instrument’s development history; they are not results from the three prospective windows.

*Table [NUMBER PENDING]. The refusal record to date during instrument development. Mechanism counts overlap and must not be summed.*

| Record | Verified development history |
|---|---|
| Whole-window decisions | 13 window roots: 6 passed and 7 failed. The append-only logs contain 16 decision rows—6 passed and 10 failed—because two windows were evaluated more than once. |
| Member collection | 1,173 executed attempts; 44 refused occurrences: 43 failed during collection and 1 completed but was refused by strict evidence validation. |
| Pre-window admission | 138 campaign prechecks: 136 admitted collection and 2 stopped before the first member. |
| Environment and supersession | 7 supersession records preserve 8 replaced attempts after background processor activity, display or login disturbance, or an operator wake event. |
| Calibration and drift | 1 inconsistent calibration and 2 missing calibration brackets. Bracket or drift evidence contributed to 8 failed decision rows across 5 roots, including 2 stale-drift verdicts. |
| Clock and validation | 3 unresolved clock-anchor occurrences. Custody, validation, or membership failures contributed to 9 failed decision rows across 6 roots. |
| Not observed | 0 active duplicate-occurrence refusals and 0 below-floor claim refusals; all 138 campaign verdicts left claim readiness unassessed. |
| Causal-reason coverage | Occurrences: 14 of 44 (31.8%). Distinct member identities: 13 of 38 (34.2%). Thirty refused occurrences retain no reconstructable cause. |

The record therefore proves that refusals happened far more reliably than it explains why each member was refused. Of the 44 refused occurrences, 14 have a reconstructable cause: 8 from machine-readable codes and 6 only from free text—1 validation explanation and 5 supersession explanations. The remaining 30 preserve a failed or invalid status but no causal explanation. This is a limitation of the development record, not a reason to omit it, and it motivates recording a structured causal reason at the point of every refusal.

The two completeness rates answer different questions. Occurrence-level accounting treats each refused attempt separately, yielding 14 of 44 (31.8%). Identity-level accounting collapses repeated attempts for the same member within a campaign, yielding 13 of 38 (34.2%). These denominators are different, and neither result is derived from the other.

One reconstructable case remains illustrative: an end-of-night re-evaluation refused a window because one member’s internal clock alignment could not be resolved. Independent adjudication upheld the refusal, and the result remained non-claim-bearing. The three prospective windows will add their own admissions, attempts, refusals, supersessions, whole-window decisions, and causal-reason coverage to this record. **[PENDING THREE PROSPECTIVE WINDOWS]**

## After the three windows

Update the bracketed marker only after all three windows have final verdicts and their logs have been audited. Then:

- Preserve the development-history counts as the dated baseline; report the prospective additions and combined totals separately.
- Recount window roots and decision rows independently, since retries may create more decision rows than roots.
- Add the new admission, attempt, refusal, supersession, calibration, drift, clock, validation, duplicate, and below-floor counts.
- Recalculate occurrence-level and identity-level reason coverage independently, retaining both fractions and percentages.
- Renumber this table and the existing results tables.

No files were changed.
