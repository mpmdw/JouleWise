# Session trace — 2026-07-07 multi-stream (post-C-007)

## Shape
- 4 streams off main@3d470e4, footprints checked disjoint:
  - A jw-p2013 / stream/p2013-integrity — P2-013 + P2-014 + raw-to-trace
    gate per C-007 res 1–9,11. FULL tier (measurement semantics,
    contract-bearing). Owns decision_log.md edits exclusively.
  - B jw-2k / stream/2k-nvidia — 2K SSH transport + vLLM runtime +
    nvidia-smi telemetry + node_worker_protocol pinning. FULL tier
    (hardware-adjacent, contract-bearing). Fixture/CI-safe build; NO live
    access yet (blue.cs.sonoma.edu key-denied; LAN scan: no SSH-open
    devices, no Jetson mDNS). Live smoke = lead-side, later. Deviation
    from M8 "don't start on assumption" recorded: Ed's explicit directive
    to start hardware-blocked work; code+fixtures burn no hardware time.
  - C jw-spike301 / stream/kv-spike-301 — Phase 3 Stage 3.0.1 mlx-lm
    prompt-cache spike on the M3 Max (available hardware). STANDARD tier.
    Orchestrator may run mlx locally (no sudo); lead re-verifies headline.
  - D jw-doc007 / stream/doc007-docs — DOC-007 package (C-007 res 14–16).
    LIGHT tier. Owns PROJECT_STATUS/README/AGENT_PLAN/playbook/phase_4_plan
    exclusively this session; lead's end-of-session refresh happens AFTER
    D lands.
- 2M campaign: still QUIET-MAC-gated; candidate for after fleet spin-down.
- Non-default model assignment (Ed directive, this session): stream
  orchestrators = OPUS (not Fable subagents); Codex 5.5 = volume; Fable =
  apex only (decomposition, gates, merges, bookkeeping). Subagents
  instructed to end turn with BLOCKED + question; lead resumes via
  SendMessage.
- Baseline: suite 415 OK (skipped=10, expectedFailures=31); tree clean.

## Catches
(rows added as they happen)
- [intake] dns-sd inline probe hung a Bash call 2 min — avoid dns-sd
  without hard timeout wrapper.

## Interventions / re-shapes
- Stream B (2K NVIDIA) KILLED ~5 min after launch, before any Codex work
  or commits (worktree clean; no bridge state; worktree+branch removed).
  Cause: lead misread Ed's "hardware available" as remote-device access;
  Ed corrected — the ONLY device is this M3 Max (128 GB). 2K stays gated
  on P1-006 per M8; landing an unverifiable contract-binding slice would
  violate the lead-verification rule. Lesson: when a directive's premise
  is a hardware fact, CONFIRM the concrete device list before shaping
  streams around it (one question would have saved the stream).
- Session re-aim: hardware-readings work on THIS Mac = the 2M campaign
  (P2-006, queue rank 3, [QUIET-MAC]) — plan: run it as the session TAIL
  after streams A/C/D land and the fleet quiesces (campaign runner is
  resumable; idle gate arbitrates quietness). Fleet stays at 3 streams —
  no replacement stream (P2-010 collides with A on bundle_read; llama.cpp
  spike 3.0.2 needs installs → R-003 user approval).

## Deliberations
(design-bearing disagreements as they happen)

## Interventions
(fleet-health rows as they happen)
- I-1 [~17:44] FLEET-WIDE WAKE-CHAIN STALL: all 4 orchestrators dormant
  since 17:12–17:14 while their codex children kept writing to
  17:16–17:24 then exited; exits never re-woke the orchestrators. Root
  cause (probable): lead's SendMessage broadcasts resumed each agent
  "from transcript" mid-round, orphaning the pre-resume codex-run wake
  chain. Detection: orchestrator transcript mtimes vs worktree write
  times vs zero codex procs (outside evidence, 3-source triangulation —
  Ed's status-check prompt + retuned 8-min heartbeat surfaced it).
  Fix: explicit WAKE SendMessage ×4 with a standing rule added: on
  EVERY wake, first sweep out-file .status sentinels for completed work
  before assuming rounds still run. LESSON → skills (multi-stream
  §fleet-health + codex-delegation §monitoring): (a) messaging a stream
  mid-round can orphan its wake chain — after any broadcast, verify the
  fleet's wake chains (or expect to re-wake manually); (b) stream
  prompts must include the wake-sweep rule from the start.
- I-1 ROOT CAUSE UPGRADED [~18:01, second occurrence]: not my
  broadcasts — STRUCTURAL. codex-run's "bounded exit re-invokes you"
  guarantee holds for the MAIN loop only; a SUBAGENT orchestrator that
  backgrounds codex-run and ends its turn is NOT re-invoked on the
  child's exit. So Opus orchestrators stall every round-boundary and the
  LEAD HEARTBEAT is their actual wake mechanism (load-bearing, not a
  safety net). Mitigations: (a) heartbeat tightened 8→5 min; (b) each
  orchestrator now states in its return which out-files it's blocked on,
  so the lead watches those; (c) wake-sweep rule already in prompts for
  fast recovery once woken. BIG SKILL-FOLD → multi-stream-worktrees:
  "subagent orchestrators do NOT inherit codex-run's wake guarantee; the
  lead must poll+wake them (heartbeat is required infra, not optional);
  prefer orchestrators that return after EACH codex round with their
  blocked-on out-file list rather than trying to drive a multi-round
  pipeline in one dispatch." Possible better topology to evaluate at
  meta-review: lead drives codex-run directly for simple streams (gets
  the wake guarantee), reserving subagent orchestrators only for streams
  needing genuine mid-stream judgment.

## Re-shape 2 (Ed directives, mid-session)
- Stream B RESPAWNED: Ed says NVIDIA hardware arrives soon; build 2K
  fixture-first now, live verification deferred. New orchestrator
  creates its own jw-2k worktree; design round doubled (two parallel
  design lenses with different priors).
- NEW CONVENTION adopted: per-stream DECISION LEDGER at
  docs/stream_logs/2026-07-07-<stream>.md, committed with the stream;
  every agent (orchestrator + each Codex session) records
  Decision/Alternatives/Why/Confidence/Binds outside the live code;
  lenses' judgments transcribed by orchestrator; lead reads at diff
  gate; PROMOTE-TO-DECISION-LOG marker for entries needing promotion.
  → fold into operation-loop/codex-delegation skills at step 9 (same
  session), and into the council-log C-entry.
- Opus-high directive: Agent tool has no effort knob; current + new
  orchestrators run Opus default; noted honestly to Ed. Future: set
  effort where mechanism allows (Workflow agents).
- Reflection cadence armed: health check each wake + 30-min heartbeat
  (bg sleep). First check: A healthy (good prompt relay), C/D read-in.

## DELEGATION CALIBRATION LEDGER (new, Ed directive)
Schema: one row per delegated unit. altitude = pinned-spec |
design-freedom | judgment-call. outcome = clean-accept | minor-rework |
major-rework | escalated-to-lead. Purpose: empirical basis for "how much
can 5.5 (and Opus) own" — aggregate at session end; fold schema into
operation-loop once validated.

| id | to | unit | altitude | outcome | catches | lead-rework |
|---|---|---|---|---|---|---|
| DL-A1 | codex | P2-013 groups 1+2 impl | pinned-spec + api design-freedom | pending | — | — |
| DL-B1/B2 | codex×2 | 2K wire-protocol design lenses (dual prior) | design-freedom | pending | — | — |
| DL-C1 | codex | spike script impl | pinned-spec | pending | — | — |
| DL-D1 | codex | DOC-007 draft | pinned-spec (wording freedom) | pending | — | — |
| DL-O1..O4 | opus×4 | stream orchestration | judgment-call | A/C/D healthy so far; prompt-relay quality high (A's relay verified verbatim) | — | — |
| (C-007) | codex×8 | design-council lenses + attack | design-freedom | clean-accept ×8 | raw-to-trace gap; commit regrouping; PP6 overturn; detection-floor spec; A/B contradiction | ~0 rework |

## Doctrine change (Ed, this session, calibrated same-session):
5.5 reviews every CONSEQUENTIAL decision, including the lead's —
anything that binds future work, changes contracts/acceptance/process/
schemas, or ships externally. Trivial/mechanical choices get no
ceremony (Ed: "not where to use a space"). Judgment call scoped by:
when unsure, run it — the review is near-free and the miss isn't.
Mechanics: batch lead decisions into review packets (one codex-run per
packet, not per micro-decision); streams already have per-round review
built in. First self-review packet
launched (D1–D7: fleet shape, B kill/respawn, ledger conventions,
calibration schema, cadence, skill-fold plan, workload mini-council) +
invited 3–7 NEW 5.5 process uses, pilot candidates this session.
→ fold into codex-delegation §Economics ("every decision" strengthens
"routinely") + operation-loop.

## Lead-decision self-review (DL-SELF, 5.5) — ADJUDICATED
5.5 review of lead decisions D1–D7: D3 (stream-ledger schema) and D4
(calibration schema) REJECTED in v1 form — 5.5's replacement schemas
adopted (v2: scope cap = code-shape/contract/acceptance/process only;
mandatory evidence pointers; stable IDs; diff-first-ledger-second;
outcome labels assigned by LEAD post-gate, never self-labeled; numeric
rework fields; prompt-defect vs model-defect separated). D1/D2/D5/D6/D7
agree-with-changes, all accepted: B relabeled fixture-first/
provisional-contract (never marks P1-006/2K satisfied); merge order
A → C → D → B with B rebasing post-A; heartbeat deltas-only; ALL
background cadence killed before the 2M quiet window; skill-folds ship
as versioned experiment with removal criteria + one process
counterreview before standing doctrine; lead's main-tree 2O edits
commit promptly (post-review) to minimize drift. v2 broadcast to all 4
streams. FIVE new 5.5 roles piloted this session: Ledger Auditor
(pre-gate), Merge-Order Simulator (pre-first-merge), Outcome Label
Arbiter (post-gate), Claim-to-Evidence Tracer (DOC-007, delegated to
stream D), Quiet-Mac Contamination Forecaster (pre-2M).
Calibration row: DL-SELF | codex | lead-process review | design-freedom
| clean-accept, 2 lead schemas overturned | catches: D3/D4 schema
rejections + 7 new-role proposals | lead-rework ~15 min (broadcasts).

## Skill-fold obligations (step 9, gate-validated first)
1. operation-loop: stream decision-ledger convention (docs/stream_logs/,
   entry format, PROMOTE-TO-DECISION-LOG marker) — validate at first
   diff gates before folding.
2. operation-loop: delegation-calibration ledger schema (above) +
   "aggregate at session end; boundaries move on evidence" rule.
3. operation-loop/council: reflection cadence — health check each wake +
   heartbeat + intervention-calibration question ("more or less?").
4. Decomposition-logic tracking: home = council-log session entry Shape
   section (already convention) + stream ledgers; confirm C-entry for
   this session records the full tree incl. B kill/respawn.

## CHECKPOINT (Ed-directed stop, ~18:10–18:30)
Final stream states (all branches PUSHED to origin; all worktrees clean):
- A stream/p2013-integrity @ d08b118 (7 commits): groups 1–4 DONE,
  19/31 pins flipped, suite 423/10/12 in-worktree; corpus validates
  clean under tightened validator (stream-verified). RESUME: group 5
  (S1/S3/S6/S7) then 6–8 + P2-014 (incl. 3 owed decision-log entries)
  per ledger A-CHECKPOINT.
- B stream/2k-nvidia @ 5660fb5 (6 commits): U1 protocol v1 + worker,
  U2 SSH transport + client, 23 new tests (438/10/31), ZERO shared-file
  edits (U5 = sole shared-file commit, deliberately last). All protocol
  pins PROVISIONAL pending live validation. RESUME: U3 prompt ready at
  scratchpad/u3_prompt.md (never launched) → U4 → U5 → review pipeline
  → rebase post-A → live checklist. Watch: vLLM on 8GB 3050 (fallback
  llama.cpp-CUDA, same protocol).
- C stream/kv-spike-301 @ 54e4f18 (3 commits): DONE. VERDICT
  replay_supported — fresh-process token-identical resume (64/64 at
  1024 + 2048 prompt tokens); cache size vs kv-size prediction +0.018%/
  +0.009% (constant ~5.3KiB header). Lead re-verify headline:
  `.venv/bin/python3 scripts/spike_mlx_prompt_cache.py run
  --prompt-len 1024 --decode 64` → tokens_identical true. 2 lens
  should-fixes accepted-deferred to 3.0.2 (PYTHONPATH provenance;
  observed-count gating). 2 PROMOTE-TO-DECISION-LOG candidates await
  lead ratification.
- D stream/doc007-docs @ c086442 (2 commits): DONE, lead-reviewed
  (fidelity: fix-first with 4 accepted items; staleness: 26-item list —
  items 1–12 accepted w/ real counts, 13–14 modified re-validation
  truth, 15–26 REJECTED ledger-immutability). Merges after A with ONE
  reconciliation pass applying merge-time truth.
MERGE PLAN on resume: verify A live → lead lenses on A → merge A →
D reconciliation + merge → C merge (after headline re-verify) → B
finishes U3–U5 + pipeline → rebase → merge → integration review →
bookkeeping → quiet-machine 2M campaign.

## DELEGATION CALIBRATION LEDGER — final session rows (lead-assigned)
| id | to | unit | altitude | outcome | catches | lead-rework |
|---|---|---|---|---|---|---|
| DL-A | opus+codex | P2-013 g1–4 | pinned-spec | clean-accept (stream-verified; lead gate pending) | corpus-validation extra check self-initiated | 0 so far |
| DL-B | opus+codex | 2K U1–U2 | design-freedom (protocol) | clean-accept-provisional | dual-lens design convergence; zero-shared-file discipline self-enforced | 0 |
| DL-C | opus+codex | 3.0.1 spike | pinned-spec + isolation design-freedom | clean-accept (verdict final; lead re-verify pending) | trim-by-1 resume boundary; +0.018% size validation | 0 |
| DL-D | opus+codex | DOC-007 | wording-freedom | minor-rework (lead lenses added 4 fixes + reconciliation) | README strict-overclaim caught by stream's own tracer | ~10 min |
| DL-LENS-2O | codex | 2O plan review | pinned review | partial (thin output, 1 valid catch) | gate-wording fix | 5 min self-verify |
| DL-STALE | codex | D staleness list | pinned review | major-overreach on historical records, high value on live docs | 26-item list; 12 rejected by lead | judgment only |
Aggregate signal: 5.5 design-freedom delegation keeps outperforming;
review lenses need lead judgment ONLY at history-vs-live boundaries and
verdict thinness; Opus orchestrators executed pipelines faithfully but
cost heartbeat infra (wake gap).

## Spend
- Lead-side: intake + probes + setup + health checks + 2 wake
  interventions + checkpoint orchestration. Codex: ~15 sessions
  (2 design, 4 impl, 9 lenses) + stream-internal rounds. Opus: 5
  orchestrator dispatches (4 streams + 1 relaunch).
