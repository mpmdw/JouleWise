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
session id: 019fdd09-759f-7290-99c6-129b744f9693
--------
user
OPERATOR PACKET DRAFT (read-only repo; write no files; final message = the packet draft in markdown). Draft the THREE-NIGHT OPERATOR PACKET for Ed: the human-facing checklist for three fresh quiet measurement windows (decision D-117 at the end of docs/decision_log.md: fresh 1.5B decode floor; fresh 7B decode floor; fresh 1.5B-vs-7B decode contrast; prefill floor cells ride the two floor windows). Source the real mechanics from docs/phase_2/window_c_operator_checklist.md, docs/phase_2/window_runbook.md (esp. section 5A physical steps, network-time toggle/sudo, display sleep, settling), and the campaign protocol. Shape: per-night one-page checklist — T-minus prep (desk-frozen artifacts verified, configs named [PLACEHOLDER ids where plan freeze pending]), arm sequence (quit agent apps, 5A steps, launch command shape, walk away), what runs unattended and roughly when (calibration bracket, references 3/1/3, science stages, post calibration) with [BUDGET] placeholders for the plan-freeze numbers, morning steps (custody backup, verdict, what to send the agent), plus an ABORT page: what a failed night looks like and what NOT to do (never delete, never retry without cause identified). Plain language, no internal decision IDs, Ed-facing. Note explicitly which steps require Ed PRESENT vs remote.
codex
I’ll trace the packet directly to the operator checklist, runbook, campaign protocol, and the final decision-log entry. I’ll keep the repository strictly read-only and return only the finished Ed-facing packet.
exec
/bin/zsh -lc "pwd && rg --files -g 'AGENTS.md' -g 'RUN_STATE.md' -g 'TASK_QUEUE.md' -g 'docs/agent_playbook.md' -g 'docs/decision_log.md' -g 'docs/phase_2/window_c_operator_checklist.md' -g 'docs/phase_2/window_runbook.md' -g '*campaign*protocol*' -g '*campaign*'" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
site_capsule/AGENTS.md
AGENTS.md
joulewise/campaign_provenance.py
RUN_STATE.md
scripts/run_campaign.py
TASK_QUEUE.md
docs/agent_playbook.md
docs/decision_log.md
tests/test_run_campaign.py
docs/phase_2/splitwise_decode_campaign.md
docs/phase_2/window_runbook.md
docs/phase_2/window_c_operator_checklist.md
tests/fixtures/campaign_policy_test.json
docs/stream_logs/2026-07-08-precampaign-review.md
docs/run_reports/2026-07-10-p2041-campaign-verdict-split.md

exec
/bin/zsh -lc 'git status --short --branch && rg -n "''^(#|##|###) |ACTIVE_STOP_CARD|Current Project Status|Known Workspace State|What Is Next" RUN_STATE.md && rg -n "''^(#|##|###) |Current Queue|Do-Not-Do-Yet" TASK_QUEUE.md && rg -n "Mission M0|M0" docs/agent_playbook.md && tail -n 180 docs/decision_log.md' in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
## main...origin/main
1:# JouleWise Run State
16:## ⏳ 2026-08-07 — paper-first session (LIVE; interim block, refreshed mid-flight)
47:## ✅ CHECKPOINT 2026-08-06 late — machine-move stop (resume script)
101:## ⏳ 2026-08-06 AFTERNOON — re-mint fork: historical consumption is closed at main; Ed's ruling owed
156:## ✅ CHECKPOINT 2026-08-06 morning — executed by the afternoon session above
242:## ⏳ 2026-08-05 LATE NIGHT — Fable resume: all 4 audits harvested, D-115 adjudicated, two Sol rounds in flight
299:### Overnight progress ledger (updated ~23:50; all evidence in .desk + session scratchpad, custody commits as noted)
342:### D-079 ISSUANCE HELD by cold gate (recorded ~03:30 2026-08-06) — issuance is IMPLEMENTATION, not an edit
369:### GOVERNING PRIORITY STACK (Ed, 2026-08-06) — all work serves the paper
378:### SYLLABUS ANCHOR (Ed, 2026-08-06) — the overarching goal
388:### QG census — magistrate stop-condition set (recorded ~02:40 2026-08-06)
407:### ESCALATION TRIGGER FIRED — quiet-guard observation-failure→absence class (recorded ~01:15 2026-08-06)
423:### Ed directive batch (2026-08-05 ~22:00, in-thread; 12-hour autonomous window)
445:## ✅ CHECKPOINT 2026-08-05 night — Ed model-switch stop (successor is FABLE; read this, then the EVENING queue)
453:### What landed this session (pushed; main green at `b55008f`)
472:### IN FLIGHT at checkpoint — harvest, do NOT re-run blind
504:### Next substantive item (un-gated payoff)
512:### Standing facts unchanged
518:## ✅ CHECKPOINT 2026-08-05 evening — DESCOPE + RESUME SCRIPT (still-valid queue; NIGHT block above updates it)
531:### SUCCESSOR'S QUEUE — start here, all agent-startable desk work
548:### What landed this session (all pushed; main green)
565:### IN FLIGHT at checkpoint (harvest from disk — do NOT re-run blind)
579:### DESCOPE — what is SHELVED (do not build; reopen only on Ed's word)
591:### Design record worth keeping (from the credential consult, before descope)
605:### Follow-on rows to register (queued this checkpoint)
621:### Standing operating facts (unchanged, still binding)
638:## ✅ 2026-08-05 — Ed's decision batch executed (PR #100 merged; acks recorded; quiet-guard ruled)
681:## ✅ CHECKPOINT 2026-08-04 ~06:30 — Ed-ordered stop (successor script)
726:## ✅ CHECKPOINT 2026-08-04 early AM — T3 HANDOFF (successor script)
739:### What landed overnight (all pushed; nothing dangling)
845:### ED OWES (nothing blocks the successor's queue)
865:### Standing operating facts for the successor
884:## ✅ CHECKPOINT 2026-08-03 late night — T3 CUTOVER (successor session, ACTIVE)
1021:## ✅ CHECKPOINT 2026-08-03 night — 16h-runway stream state (successor is FABLE, MAGISTRATE, on T3 Code)
1129:## DESK-SESSION UPDATE (HISTORICAL — superseded by the checkpoint block at top) (2026-08-03, Ed away — first the cold-gate arc, then a sleep-window of non-claim rows) — read this, then the two ⏸️ blocks above
1221:## EXECUTED RESUME SCRIPT (2026-08-02 ~16:10 PT checkpoint — FULLY EXECUTED by the 2026-08-03 desk session; see the DESK-SESSION UPDATE above; retained as historical record)
1350:## PRIOR RESUME SCRIPT (2026-08-01 desk session, second checkpoint; resume EXACTLY here)
1451:## PRIOR ACTIVE RESUME SCRIPT (2026-08-01 ~07:00 PT checkpoint; EXECUTED this desk session — retained for the collection facts)
1559:## PRIOR ACTIVE RESUME SCRIPT (2026-07-31 ~22:15 PT checkpoint; EXECUTED — window A verdict emitted [FAILED], window B run and salvage-closed; retained for the collection facts)
1663:## PRIOR STATE (2026-07-31 claims-desk close-out; resume script below FULLY EXECUTED)
1755:## EXECUTED RESUME SCRIPT (2026-07-30 19:15 PT pre-window checkpoint; historical — fully executed, see CURRENT STATE)
1834:## PRIOR STATE (2026-07-30 afternoon; the resume script below is EXECUTED except where struck)
1856:## EXECUTED RESUME SCRIPT (2026-07-30 ~11:00 PT handoff checkpoint; historical)
1984:## Start Here For Every Big Run
2004:12. If an `ACTIVE_STOP_CARD` exists below, it overrides every normal
2033:## Historical Stop-Card Note
2039:## ACTIVE_STOP_CARD
2043:## Active Global Work-Selection Gates
2047:## Restart By Machine-State Lane
2051:### [ED-EXTERNAL]
2055:### [QUIET-MAC]
2059:### [AGENT]
2065:## CHECKPOINT 2026-07-18 (late): D-077 adversarial arc complete, PR #77 open
2089:## CHECKPOINT 2026-07-18: Claude script bridge runs in the pet's app task
2115:## CHECKPOINT 2026-07-17 (late session): env-guard branch open, review pending
2166:## Superseded stop card (CP-5)
2178:## Current Project Status
2185:### The central measurement fact (read before any measurement decision)
2197:### Collection state
2231:### The critical path: build the mint (HISTORICAL — CLOSED 2026-07-30)
2266:### Disk
2290:### Orchestration
2298:### What needs Ed
2377:## Session History (pointers only — run reports own the narrative)
2499:## Current Verification
2596:### Historical verification archive (exact at the recorded heads)
2739:## Known Workspace State
2806:## Historical Next-Work Snapshot (superseded 2026-07-15)
2824:## Reference Decisions And Blockers (non-selection context)
1:# JouleWise Task Queue
6:## Intake Rule For New Tasks
34:## Priority Scale
47:## Ranking Factors
65:## Ready/Shelf Rule
80:## Machine-State Lanes (adopted C-007, 2026-07-07)
92:## Historical Queue Snapshot (superseded 2026-07-15)
96:Current Queue region is the sole live work-selection view.
98:## Completed Queue Items
184:## Shelved Follow-Ups With Triggers (C-027 disposition ledger — REV-10)
213:## Current Do-Not-Do-Yet List
241:## Queue Maintenance
254:## Intake Batch Owed To The Kernel (2026-07-30/31)
306:## Current Queue
384:## Active Global Work-Selection Gates
388:### [ED-EXTERNAL] lane
399:### [QUIET-MAC] lane
412:### [AGENT] lane
462:### Shelved task records
26:1. Run Mission M0 (preflight) — always.
50:## Mission M0: Preflight (every session)
472:The M0 step-6 handoff list, plus: if you changed an adapter or bundle
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
/bin/zsh -lc "sed -n '1,90p' docs/agent_playbook.md && sed -n '1,110p' RUN_STATE.md && sed -n '1984,2065p' RUN_STATE.md && sed -n '2178,2376p' RUN_STATE.md && sed -n '2739,2805p' RUN_STATE.md && sed -n '1,95p' TASK_QUEUE.md && sed -n '213,250p' TASK_QUEUE.md && sed -n '306,430p' TASK_QUEUE.md" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
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

## ⏳ 2026-08-07 — paper-first session (LIVE; interim block, refreshed mid-flight)

**Ed's directives this session:** (1) abandon t3 work; (2) MVP capstone
paper FIRST, rest later; (3) 14h autonomous window; (4) three quiet
nights + desk work accepted as the path → **D-117 transcribed+pushed**
(D-110 re-mint order superseded; three prospective windows; prefill
floors ride floor windows; contrast decode-only; 256-tok prefill arm
still Ed's option); (5) Workflow license for non-serial desk work.

**DONE this session (all pushed):** checkpoint resume items 2-4 —
T3-CHAR-PAIR r01/r02 analysis banked (`fc48b1b`, dormant floor 0.192 W,
NON-CLAIM); prefill feasibility scout MARGINAL-at-128-tok custodied
(`docs/process_traces/2026-08-07-prefill-feasibility/`); C-049 marathon
council record (`03841c8`); skill-usage log; D-117 (`dbb9685`);
CLAIMS_STATUS un-staled (`a1f0e19`).

**IN FLIGHT (harvest, do not re-run):** (a) paper fix round on branch
`impl/paper-mvp-complete` — Sol xhigh, WRITE_SCOPE
docs/paper/draft-v1.md, closing round-2 findings (lens A 3 blockers:
tense, two-gate rule collapse, prefill-marginality misstatement; lens B
11; F-BIB-1) — review records + bibliography audit custodied on the
branch (`3542265`, `1892edc`); on harvest: lead diff gate → delta
re-audit → PR → merge on green (D-072). (b) Plan-freeze design consult
(Sol xhigh, read-only, scratchpad desk worktree) for the three-window
packet → on return: lead ratify → enforced-scope implementation units →
adversarial review → PR(s). Then: three-night operator packet for Ed;
end-of-session sweep + run report.

**Worktrees:** `<session-scratchpad>/desk` (main, bookkeeping) — prune
at close. Main tree holds `impl/paper-mvp-complete`.

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
   (instrument arc, acceptance rule, tooling, process record) stands.

**RESUME ORDER for the successor:**
1. If Ed has ruled the fork → transcribe the decision (supersede/amend
   D-110 + D-113 rewire per SYNTHESIS.md) and start the Option-2 desk
   queue (AFTERNOON block bottom). If not ruled → he owes: fork ruling,
   prefill-contrast shape ack, three-nights scheduling.
2. T3-CHAR-PAIR r01/r02 desk analysis (the dormant-app number) — cheap,
   answers his live question, informs any zero-agent-rule revisit.
3. Prefill-contrast feasibility desk check from historical diagnostics
   (labelled, non-claim).
4. End-of-session bookkeeping STILL OWED from the marathon session:
   consistency sweep, council log, skill-usage log.

## ⏳ 2026-08-06 AFTERNOON — re-mint fork: historical consumption is closed at main; Ed's ruling owed

**PR #109 merged on green** under D-072 at the gate-reviewed head
`d85b4f9` (no post-review commits; ledger + custody backup verified
byte-identical to the checkpoint sha before merge). `d079recon`
worktree + local branch pruned. All three D-110 conditions were thereby
satisfied — and the FIRST consumption attempt exposed a structural
block.

**THE FINDING (full record:
## Start Here For Every Big Run

Before starting substantial work:

1. Read this file.
2. Read `TASK_QUEUE.md`.
3. Read `AGENT_PLAN.md` (phase index) and the active phase's plan doc under
   `docs/phase_N/`; per-item status lives in the phase exit checklist
   (D-023).
4. Read `docs/planning_reflection_protocol.md`.
5. Check `docs/decision_log.md` before re-deciding anything; check
   `docs/risk_register.md` if starting a phase or a hardware-dependent task.
6. Check the last 2-3 commits with `git log --oneline --decorate -3`.
7. Check `git status --short --branch`.
8. Run `python3 -m unittest discover -s tests` unless the task is docs-only.
9. Do not commit local deletions or unrelated changes unless the user asks.
10. Heartbeat rule (`docs/milestones.md`): if >14 days passed with no run
    report and no recorded break, start with a milestones + risk review.
11. Live MLX gates use the repo venv: `.venv/bin/python -m joulewise ...`
    (system python3 lacks mlx → `runtime_unavailable`).
12. If an `ACTIVE_STOP_CARD` exists below, it overrides every normal
    "restart", "next", queue, and mission pointer until explicitly cleared.

At the end of substantial work:

1. Update only hand-authored factual/history sections of this file.
2. Update `docs/process/state_kernel.json` for live task state and regenerate;
   do not hand-edit either generated region.
3. Add or update a detailed report in `docs/run_reports/`.
4. Record tests, commands, and blockers; generated lane heads own next-work
   selection.
5. Record new decision-log entries and any risk-register status changes.
6. Refresh `PROJECT_STATUS.md` if advisor-visible state changed.
7. Push green commits promptly (small doc/bookkeeping commits straight
   to main; multi-commit code series as branch + PR per D-031). Do not
   accumulate unpushed local state — the remote and the high-level docs
   (README, PROJECT_STATUS) are the user's and advisor's view.
8. Run a docs-consistency sweep before the final bookkeeping commit
   (delegate to a fast subagent): stale test counts, gate-state
   contradictions between prose summaries and checklist matrix rows,
   numbers cited in multiple places (C-002; D-023 extension).
   Refreshing `docs/site/DRIFT.md` is OPTIONAL (D-101: the site gates
   nothing and is fully decoupled); when touched, it informs only:
   per D-068 (2026-07-14) NO agent regenerates or deploys the site,
   ever — automation informs; Ed deploys manually. (Supersedes the
   C-013 regenerate+redeploy convention.)
9. Call out any dirty working-tree state that should not be accidentally
   committed.

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

## Historical Queue Snapshot (superseded 2026-07-15)

The former hand-authored live table was removed because it duplicated kernel
tasks. Dated completion and disposition history remains below; the generated
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

exec
/bin/zsh -lc 'wc -l docs/phase_2/window_c_operator_checklist.md docs/phase_2/window_runbook.md docs/phase_2/splitwise_decode_campaign.md && rg -n "''^(#|##|###|####) " docs/phase_2/window_c_operator_checklist.md docs/phase_2/window_runbook.md docs/phase_2/splitwise_decode_campaign.md' in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
     365 docs/phase_2/window_c_operator_checklist.md
    1009 docs/phase_2/window_runbook.md
     557 docs/phase_2/splitwise_decode_campaign.md
    1931 total
docs/phase_2/splitwise_decode_campaign.md:1:# Splitwise-vein decode contrast campaign (splitwise_decode_v1) — FROZEN PLAN DRAFT
docs/phase_2/splitwise_decode_campaign.md:18:## 1. What is authored and where
docs/phase_2/splitwise_decode_campaign.md:43:## 2. BLOCKING FINDING — the contrast is collectible tonight but not claimable
docs/phase_2/splitwise_decode_campaign.md:50:### Blocker A — the 7B arm has no floor, and floor transport is stack-bound
docs/phase_2/splitwise_decode_campaign.md:105:### Blocker B — no analysis-manifest schema can express a model-vs-model contrast
docs/phase_2/splitwise_decode_campaign.md:128:### What this does and does not mean
docs/phase_2/splitwise_decode_campaign.md:137:### Option set for the magistrate (§10 Q1)
docs/phase_2/splitwise_decode_campaign.md:155:## 3. Model artifact status — FINALIZED
docs/phase_2/splitwise_decode_campaign.md:190:## 4. Duration arithmetic — measured probe, not model-size inference
docs/phase_2/splitwise_decode_campaign.md:209:### O2 — contrast window (`splitwise_decode_v1`, 40 members: 20 A + 20 B)
docs/phase_2/splitwise_decode_campaign.md:225:### O1 — 7B floor window (`qwen25_7b_decode_floor_v1`, 50 members, all 7B)
docs/phase_2/splitwise_decode_campaign.md:248:## 5. Pre-registration sheet — DRAFT, CONDITIONAL on §2
docs/phase_2/splitwise_decode_campaign.md:256:### 5.1 `splitwise_decode_v1` — cross-model decode contrast
docs/phase_2/splitwise_decode_campaign.md:300:### 5.2 `qwen25_7b_decode_floor_v1` — 7B decode floor calibration
docs/phase_2/splitwise_decode_campaign.md:319:## 6. Operator checklist delta vs `docs/phase_2/window_runbook.md`
docs/phase_2/splitwise_decode_campaign.md:383:## 7. Validation record (lead-run, 2026-07-29)
docs/phase_2/splitwise_decode_campaign.md:463:## 8. Evidence base carried forward from the checkpoint (re-verified)
docs/phase_2/splitwise_decode_campaign.md:488:## 9. What changed from the checkpoint
docs/phase_2/splitwise_decode_campaign.md:502:## 10. Open questions for magistrate ratification
docs/phase_2/window_runbook.md:1:# Quiet-Mac Claim-Window Run-Book
docs/phase_2/window_runbook.md:26:## 1. Rules that do not bend
docs/phase_2/window_runbook.md:65:## 2. The post-PR #85 compatibility gate is satisfied
docs/phase_2/window_runbook.md:102:### Decision on the three flags missing from the draft chain
docs/phase_2/window_runbook.md:121:## 3. Time budget in plain language
docs/phase_2/window_runbook.md:148:## 4. Freeze the plan before quiet time
docs/phase_2/window_runbook.md:225:## 5. Machine and operator preflight
docs/phase_2/window_runbook.md:267:## 5A. Pre-window clock stabilization (administrator step; Ed performs it)
docs/phase_2/window_runbook.md:275:### What went wrong, in plain language
docs/phase_2/window_runbook.md:324:### Before the window (administrator rights required)
docs/phase_2/window_runbook.md:363:### If a single member still fails the anchor
docs/phase_2/window_runbook.md:383:## 5B. Pre-flight calibration screen (D-079 clause 3)
docs/phase_2/window_runbook.md:454:## 6. The foreground measurement chain
docs/phase_2/window_runbook.md:574:# D-079 clause 3: pre-flight calibration screen. Refuses an out-of-family
docs/phase_2/window_runbook.md:575:# pre-calibration before any member is collected. Threshold is bindings-bound
docs/phase_2/window_runbook.md:576:# (Mac15,9 / macOS 25F84 / ac_high_power / 100 ms / estimator v2); see §5B.
docs/phase_2/window_runbook.md:641:# Abort before member 1 if the pre-calibration is out of family (§5B).
docs/phase_2/window_runbook.md:644:# The reference corpus and bound are minted inside this same quiet window.
docs/phase_2/window_runbook.md:684:## 7. Display and screen governance
docs/phase_2/window_runbook.md:701:## 8. Check the fresh bound and calibration bracket
docs/phase_2/window_runbook.md:737:## 9. Emit exactly one whole-window verdict
docs/phase_2/window_runbook.md:768:### D-100 §9 amendment — explicit salvage-dangler verdict dispatch
docs/phase_2/window_runbook.md:795:## 10. Failure playbook
docs/phase_2/window_runbook.md:824:### Slot quarantine and supersession
docs/phase_2/window_runbook.md:855:### D-100 §10 amendment — terminally absent salvage is exceptional
docs/phase_2/window_runbook.md:881:### Post-calibration failure and the a10 recorded deviation
docs/phase_2/window_runbook.md:909:## 11. Back up, then extract in the same custody session
docs/phase_2/window_runbook.md:946:## 12. Close-out record
docs/phase_2/window_runbook.md:973:## 13. Open questions for Ed (recorded, not adopted)
docs/phase_2/window_runbook.md:978:### 13.1 A governed member-level retry for `clock_anchor_unresolved`
docs/phase_2/window_runbook.md:1003:### 13.2 Post-calibration retry shape for a non-clock failure
docs/phase_2/window_c_operator_checklist.md:1:# Window C Readiness and Operator Checklist
docs/phase_2/window_c_operator_checklist.md:9:## 1. BEFORE the night — desk freeze
docs/phase_2/window_c_operator_checklist.md:11:### What is already prepared
docs/phase_2/window_c_operator_checklist.md:28:### What must still be completed
docs/phase_2/window_c_operator_checklist.md:112:### Frozen operational thresholds
docs/phase_2/window_c_operator_checklist.md:128:### One night versus multiple sessions
docs/phase_2/window_c_operator_checklist.md:144:## 2. AT the machine — Ed’s T-0 gate and run
docs/phase_2/window_c_operator_checklist.md:148:### T-0 physical and machine gate
docs/phase_2/window_c_operator_checklist.md:201:### Launch and automatic run
docs/phase_2/window_c_operator_checklist.md:252:### Automatic stop rules
docs/phase_2/window_c_operator_checklist.md:266:## 3. AFTER the night — authentication, verdict, backup, extraction, and figures
docs/phase_2/window_c_operator_checklist.md:268:### Immediate close-out
docs/phase_2/window_c_operator_checklist.md:328:### Desk analysis and required C-iv figures
docs/phase_2/window_c_operator_checklist.md:342:## Known failure modes and their preventive checks
docs/phase_2/window_c_operator_checklist.md:356:## Provenance appendix

exec
/bin/zsh -lc "sed -n '1,365p' docs/phase_2/window_c_operator_checklist.md" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
# Window C Readiness and Operator Checklist

**Current verdict: NO-GO.** Window C should not be scheduled yet. The science configurations are largely prepared, but the issued calibration acceptance artifact, final Window C/D split, numerical analysis gates, extraction specification, and launcher-verified readiness record are still missing.

A clean Window C can complete an important portion of the instrument characterization. It cannot complete the full A+ characterization by itself: the prepared non-micro-delta science already requires about 3.64 hours before calibrations, references, stage settles, and the required 20% failure margin. Between-session stability also requires at least three independent sessions or days.

Status below is as inspected on 2026-08-06.

## 1. BEFORE the night — desk freeze

### What is already prepared

| Item | Status | Prepared material |
|---|---|---|
| Collection protocol | **READY** | `docs/phase_2/window_runbook.md`: two calibrations, fresh 12-member bound corpus, start/mid/end references, per-stage arm and re-probe, one verdict, backup before extraction. |
| Environment policy | **READY** | AC/external power, low-power mode off, displays asleep, screensaver disengaged, nominal thermal pressure, CPU admission, known adapter wattage. |
| Linearity membership | **READY and frozen** | 40 fresh members: prompt 128; output 128/256/512/1024/2048; eight observations per level. Plan SHA-256 `ac67019d…7166f3`. Estimated science time: 62.1 min. |
| Null-ladder membership | **READY and frozen** | 60 fresh members: output 128/512/2048; five A/B/B/A blocks per magnitude, 20 members per magnitude. A and B are identical aliases. Plan SHA-256 `7f75f73a…017da`. Estimated science time: 93.6 min. |
| Additivity membership | **READY and frozen** | 24 fresh members: prompt/output shapes 2048/128, 512/512, and 128/2048; eight members per shape. Each bundle supplies prefill, decode, and request energy. Plan SHA-256 `4c63bf9e…44133`. Estimated science time: 37.6 min. |
| Long-hold membership | **READY and frozen** | Three sustained 4096-output members plus 120/300/600-second extended-idle members. Plan SHA-256 `34af9db7…a8f2`. Estimated science time: 25.3 min. |
| Existing plan integrity | **READY** | All four sidecar hashes match their plan files. |
| ABBA calculation | **READY** | Within each block, compare the mean of the two inner B observations with the mean of the two outer A observations. ABBA reduces linear drift but does not replace the window drift allowance. |
| Hardware supply | **PREVIOUSLY PROVEN; RE-PROBE AT T-0** | The 140 W Anker supply was later observed at 28 V × 4.99 A, “pd charger,” 140 W negotiated. The earlier 70 W mismatch is historical, but the night still requires a fresh observation. |
| Repository checkout | **CLEAN NOW, NOT FINAL** | `main` and `origin/main` are at `6fddd50`; working tree clean. This cannot yet be the measurement pin because required calibration-acceptance work remains unfinished. |

All recollections must be fresh occurrences under the new Window C/D roots. Nothing from the retired Window B corpus may enter membership, calibration, reference, floor, or extraction bases.

### What must still be completed

- [ ] **Issue the production calibration-acceptance artifact.** The current file is explicitly `schema_fixture_unissued`, with a genesis ledger cutoff and `claim_eligible: false`. Complete its consumer implementation, exact-byte review, issuance, ledger/head-pin binding, and production-path verification.

- [ ] **Complete the corrected floor re-mint chain.** Require validator-clean, end-to-end evidence using the issued acceptance artifact before spending a collection night.

- [ ] **Choose and freeze the C/D split.** List every stage in exactly one window. Do not leave “spillover if time permits”; optional in-night membership is forbidden.

- [ ] **Finish the micro-delta plan.** The only generated material is a 20-member `k0064` placeholder marked `draft_pending_slope`. The paper requires predicted effects near 0.5×, 1×, 1.5×, and 3× the floor in both directions, while the current suite README speaks of three slots. Resolve that mismatch, choose the exact token increments from the preregistration slope, generate every run ID, counterbalance direction, ratify the plan, and freeze its digest.

- [ ] **Freeze the exact comparison definitions.** At minimum:

  - Linearity: gross request energy and decode energy versus runtime-observed output count, with the regression and residual calculation fixed.
  - Null ladder: identical-condition ABBA deltas at all three magnitudes.
  - Empirical floor: signed micro-deltas at every frozen floor multiple, in both directions.
  - Additivity: prefill plus decode versus enclosing request energy, with setup/gap treatment fixed.
  - Causal invariance: prefill energy versus output length while prompt tokens are fixed. The existing additivity shapes do not themselves hold prompt length fixed; either prospectively extract prefill from the fixed-prompt linearity ramp or author an additional fixed-prompt stage.
  - Drift/settling: start/mid/end trajectory plus the exact recovery comparison for the 180-second convention.
  - Stability: the exact calibration, null, and floor cells repeated in each eligible session.

- [ ] **Freeze numerical scientific acceptance rules.** The current campaign plans contain no non-null `comparisons`, `acceptance`, `analysis`, or `extraction` sections. Before collection, specify:

  - linearity lack-of-fit and residual criteria;
  - the null interval-to-floor rule;
  - which micro-delta levels must be refused and which must resolve;
  - the additivity tolerance and causal-invariance slope bound;
  - the thermal/reference recovery band supporting or revising 180 seconds;
  - the between-session stability rule and eligible identity-matched sessions.

  Do not choose these after seeing Window C outcomes.

- [ ] **Author the composite extraction specification.** It must name every expected cell, metric, member or ABBA block, condition family, minimum count, comparison orientation, drift allowance, and exact passing verdict basis. It must use only fresh Window C occurrences.

- [ ] **Freeze the calibration retry matrix.** Record these exact existing rules:

  - calibration-only `clock_anchor_unresolved`: at most one settled retry for the pre calibration and at most one for the post calibration;
  - member-level clock-anchor retry: zero;
  - non-clock post-calibration retry: zero;
  - pre-calibration level-screen cause-removal retry: enter an exact integer in the plan; the current material does not select one;
  - manual or outcome-driven retry: zero;
  - third failure on the same cause: close the window.

- [ ] **Assemble the plan root outside both runs roots.** It must contain:

  ```text
  WINDOW_PLAN_ROOT/
  ├── window.env
  ├── before_midpoint_stages.txt
  ├── after_midpoint_stages.txt
  ├── extraction_spec.json
  ├── waivers.json
  ├── retry_policy.json
  ├── analysis_acceptance.json
  ├── readiness-record.json
  └── window-chain.zsh
  ```

- [ ] **Set exact fresh paths.** Fill the date; do not leave placeholders at review:

  ```text
  WINDOW_ID=window_metrologyC_YYYYMMDD
  RUNS_ROOT=/Users/edr/code/JouleWise/runs_window_metrologyC_YYYYMMDD
  BOUND_RUNS_ROOT=/Users/edr/code/JouleWise/runs_window_metrologyC_YYYYMMDD_bound
  CUSTODY_ROOT=/Users/edr/JouleWise-window-custody/window_metrologyC_YYYYMMDD
  CLAIM_BACKUP_DEST=.../window_metrologyC_YYYYMMDD/claim
  BOUND_BACKUP_DEST=.../window_metrologyC_YYYYMMDD/bound
  ```

- [ ] **Set `waivers.json` to exactly `[]`.** The launch and verdict commands must not pass a waiver argument.

- [ ] **Pin the final code revision.** Require reviewed, merged `main`, clean checkout, exact `git rev-parse HEAD`, policy hash, issued acceptance-artifact digest, ledger-head pin, plan-tree digest, and launcher digest.

- [ ] **Run desk verification unpiped.** Require the canonical suite plus focused campaign/config, strict-validation, calibration, bound-mint, verdict, backup, and extraction checks. Save exit codes in the readiness record.

- [ ] **Validate and dry-run every stage against its intended root.** Include the bound corpus, all three reference stages, every science stage, and both prospective windows. Resolve every doctor warning rather than casually acknowledging it.

- [ ] **Prove the negative gates.** The frozen head must still refuse an awake or saver-active display, unresolved clock anchor, and missing or temporally invalid environment admission.

- [ ] **Verify model and config availability offline.** Models, tokenizer, configs, scripts, and the virtual environment must be cached and loadable without downloads during the window.

- [ ] **Create one reviewed readiness record.** It must bind the plan digest, issued calibration artifact, ledger head, clean code revision, empty waiver list, exact roots, backup destinations, dry-run results, environment preflight contract, and retry matrix.

- [ ] **Make the ordinary launcher verify that record.** `scripts/prewindow_check.sh` is useful but currently does not by itself bind the complete frozen-plan record. Until the launcher mechanically verifies it, the start fence is not satisfied.

### Frozen operational thresholds

These values are already defined, but the final chain must consume the issued artifact mechanically rather than trusting copied literals:

| Gate | Required result |
|---|---|
| Wall-versus-monotonic span | No more than `0.005 s` per member. |
| Pre-calibration fiducial | `b_fiducial_s <= 0.033558756679900`. |
| Clean calibration-bracket drift | No more than `0.010818 s`. |
| Budgetable ordinary excess | At most `0.001275166090593858 s`, for maximum drift `0.012093166090593858 s`; identified systematic defects are never budgeted. |
| Bound freshness | Minted from all 12 bound members inside this window; maximum age `86400 s`; exact OS, supply, and calibration identities must match. |
| Environment | AC and externally connected, low-power mode off, all online displays asleep, screensaver disengaged, thermal pressure nominal. |
| CPU admission | At least 30 samples; busy-ratio p95 no more than `0.5`; combined processor power p95 no more than `1.0 W`. |
| Stage failure behavior | `--max-failures 1`; only a preregistered recovery may relaunch a stage. |
| Whole window | Exactly one ordinary verdict over the exact occurrence set; `status: passed`; both energy-family screens and allowances authenticated. |

### One night versus multiple sessions

The prepared C1, C2, C4, and C5 science totals about **218.6 minutes before** two calibrations, the 12-member bound corpus, seven references, stage settles, arming, and failure margin. Therefore the full set cannot fit one compliant 2–4-hour window.

A defensible starting split is:

| Session | Candidate frozen contents | Result available if the window passes |
|---|---|---|
| **Window C** | Linearity; additivity; middle null rung; sustained-hold Part A. Add extended-idle Part B only if the measured dry-run budget still retains 20% margin. | Full linearity; additivity; causal invariance if fixed-prompt prefill extraction is authored; one null magnitude; within-window drift trajectory; partial or full settling evidence depending on Part B; stability session 1. |
| **Window D** | Remaining null rungs; finalized micro-delta slots; any deferred settling stage; exact repeat cells. | Full null ladder; empirical floor verification; completed settling evidence; stability session 2. |
| **Third session/day** | Same preregistered calibration, null, and floor repeat cells under matched recorded identity. | Minimum three-session between-session stability result. |

This split is a candidate, not permission to launch. Final packing must come from dry-run timings. If Window D cannot retain the 20% margin, move a complete preregistered stage to the third session; never compress settles or remove references.

Window B cannot count toward any replacement result. A prior session may count toward stability only if it is prospectively named, verdict-passed, exact-cell compatible, and identity-authenticated. Otherwise plan three new sessions.

## 2. AT the machine — Ed’s T-0 gate and run

Every line is binary. Any unknown, warning, or missing evidence means **NO-GO**.

### T-0 physical and machine gate

- [ ] **PASS — reviewed readiness record verifies without exception.**  
  Evidence: `$WINDOW_PLAN_ROOT/readiness-record.json` and launcher exit `0`.

- [ ] **PASS — final checkout equals the pinned commit and is clean.**  
  Evidence: `$CUSTODY_ROOT/t0/git-state.txt`.

- [ ] **PASS — approved 140 W Anker adapter and approved cable are connected.** The live observation must report external AC, “pd charger,” and 140 W negotiated; a recurrence of 70 W is NO-GO.  
  Evidence: `$CUSTODY_ROOT/t0/power-identity.json`.

- [ ] **PASS — power policy is `ac_high_power`, low-power mode is off, and the supply is not changed after this point.**  
  Evidence: `$CUSTODY_ROOT/t0/environment-preflight.json`.

- [ ] **PASS — system time is correct against an independent source before disabling synchronization.**  
  Evidence: clock-offset line in `$CUSTODY_ROOT/t0/clock-pin.txt`.

- [ ] **PASS — prior automatic-network-time state is recorded, network time is disabled, and the machine settles for 180 seconds.**  
  Evidence: `systemsetup` output and timestamps in `$CUSTODY_ROOT/t0/clock-pin.txt`.

- [ ] **PASS — Time Machine, updates, indexing, downloads, and cloud uploads have finished or are paused.**  
  Evidence: `$CUSTODY_ROOT/t0/process-census.txt`.

- [ ] **PASS — the Mac has been untouched and idle for at least ten minutes so idle-triggered maintenance can drain.** This is in addition to stage settles.  
  Evidence: start/end timestamps plus clean pre-window checks in `$CUSTODY_ROOT/t0/prewindow-check.log`.

- [ ] **PASS — no contaminating process exceeds the preflight limits and overall load is acceptable.**  
  Evidence: `scripts/prewindow_check.sh --wait ...` exit `0` and captured output.

- [ ] **PASS — passwordless `powermetrics` works.**  
  Evidence: `sudo -n /usr/bin/powermetrics ...` exit `0` in the preflight log.

- [ ] **PASS — at least the frozen minimum disk headroom is available, both backup destinations exist, and their capacity is sufficient for both roots.**  
  Evidence: `$CUSTODY_ROOT/t0/storage.txt`.

- [ ] **PASS — all models and configs load locally without downloads.**  
  Evidence: desk dry-run receipt bound by the readiness record.

- [ ] **PASS — all online displays are asleep; the screensaver is disengaged; persistent screensaver/display settings were not modified as part of the window.**  
  Evidence: `scripts/quiet_mac_prep.sh` log and post-arm probe.

- [ ] **PASS — thermal pressure is nominal.**  
  Evidence: preflight environment record.

- [ ] **PASS — Claude, Codex, t3, browser automation, browsers, periodic monitors, log tails, and other output-streaming sessions are closed.** An installed-but-inactive quiet guard does not satisfy this.  
  Evidence: independent process census with zero agent, t3, browser-automation, campaign, and watcher survivors.

- [ ] **PASS — cloud-sync custody is safe.** If `bird` is absent, record absence. If present, record PID plus process start time, verify state `T` twice, hold its launchers as prescribed, install a fail-safe `CONT` trap, and do not access Mobile Documents while it is stopped.  
  Evidence: `$CUSTODY_ROOT/t0/bird-custody.log`.

- [ ] **PASS — everyone nearby has been told not to touch the Mac, displays, lid, charger, or cable.**  
  Evidence: operator initials and timestamp in the T-0 record.

### Launch and automatic run

- [ ] **Launch exactly once from the ordinary guarded foreground shell:**

  ```sh
  caffeinate -is /bin/zsh "$WINDOW_PLAN_ROOT/window-chain.zsh" "$WINDOW_PLAN_ROOT"
  ```

  Evidence: `chain_start` in `$CUSTODY_ROOT/operator_logs/window-chain.log`.

- [ ] **After arming, send at most the one-line arm message and stop all operator output.** Do not tail logs or wake the display.

- [ ] **Pre calibration completes under protocol v3.** If its sole failure is `clock_anchor_unresolved`, the chain may settle and retry once. Any other failure follows the frozen retry matrix.  
  Evidence: both attempt directories, if two exist, and the pre-calibration log.

- [ ] **Pre-calibration level screen passes before member 1.**  
  Evidence: `pre_calibration_screen=passed` and the recorded fiducial value.

- [ ] **Twelve fresh bound-corpus members collect under the pre calibration.**  
  Evidence: bound-root campaign log and exact 12-member manifest.

- [ ] **The dual-family bound mints inside this window.**  
  Evidence: `$BOUND_RUNS_ROOT/neg8-drift-bound.json`.

- [ ] **Start reference triplet completes.**  
  Evidence: three exact start-reference occurrences in the claim log.

- [ ] **All frozen pre-midpoint science stages complete in their listed order.**  
  Evidence: `stage_start`/`stage_end` pairs and campaign manifests.

- [ ] **Midpoint reference completes.**  
  Evidence: its exact occurrence in the claim log.

- [ ] **All frozen post-midpoint stages complete in their listed order.**  
  Evidence: `stage_start`/`stage_end` pairs and campaign manifests.

- [ ] **End reference triplet completes.**  
  Evidence: three exact end-reference occurrences in the claim log.

- [ ] **Post calibration completes after the final member with at least the required post-window dwell.** Its only automatic retry is one settled retry for sole-reason `clock_anchor_unresolved`.  
  Evidence: post-calibration directory and log.

- [ ] **Every campaign invocation performs the 20-second display arm and a fresh environment re-probe.** The desk prep result is not a certificate for later stages.  
  Evidence: per-stage logs and per-bundle environment-admission records.

- [ ] **Adapter wattage remains stable from first admission through post capture.**  
  Evidence: per-observation adapter records and eventual verdict.

- [ ] **The chain records `measurement_complete`.**  
  Evidence: final timestamp in `window-chain.log`.

### Automatic stop rules

- [ ] A display wake, screensaver engagement, CPU-admission failure, operator touch, or unknown environment state loses the affected occurrence. Never use an environment override.

- [ ] A member-level clock-anchor failure is preserved and quarantined; there is no member-level anchor retry.

- [ ] A pre-calibration level failure ends the attempt before member 1. Relaunch only after a named cause was removed and only within the frozen cause-removal retry count.

- [ ] A supply or cable identity change ends the entire window.

- [ ] The third failure on the same cause closes the window.

- [ ] No threshold, waiver, membership, stage order, analysis rule, or retry policy is changed during the night.

## 3. AFTER the night — authentication, verdict, backup, extraction, and figures

### Immediate close-out

- [ ] **Wake the display only after `measurement_complete`.**

- [ ] **Finalize every calibration-ledger reservation.** No pending, abandoned-without-disposition, malformed, or conflicting observation may remain.

- [ ] **Update and commit the exact ledger-head pin before claim evaluation.** Do not evaluate between ledger advancement and the committed pin.

- [ ] **Authenticate the calibration bracket.** Require:

  - valid protocol-v3 pre and post artifacts;
  - pre before the first science member and post after the last;
  - both under the claim root’s `instrument_validation/`;
  - exact acceptance epoch and issued-artifact match;
  - same OS build, power policy, instrument identity, cadence, and estimator;
  - operative use of the larger bound;
  - clean or mechanically budgeted drift under the issued rules.

- [ ] **Authenticate the fresh bound.** Require all 12 exact members, same-window mint time, both energy families, 86400-second freshness field, and exact OS/supply/calibration bindings.

- [ ] **Record each permitted supersession exactly once before the verdict.** Two present occurrences or duplicate supersession records refuse. Do not plan on salvage to rescue a fresh window.

- [ ] **Emit exactly one ordinary whole-window verdict:**

  ```sh
  .venv/bin/python scripts/run_campaign.py \
    --whole-window-verdict \
    --runs-dir "$RUNS_ROOT" \
    --log "$RUNS_ROOT/campaign_log.jsonl" \
    --campaign-policy configs/campaign_policies/quiet_mac_p2_production.json \
    --neg8-drift-bound "$BOUND_RUNS_ROOT/neg8-drift-bound.json"
  ```

- [ ] **Require `status: passed`.** Record the evaluation-basis SHA-256, exact member-occurrence set, calibration bracket, policy hash, both family screens, both drift allowances, admitted CPU state, and stable adapter continuity.

- [ ] **Back up both immutable roots and require exit code 0 for each.** Record separate source, destination, start/end timestamps, and exit status for the claim root and bound root. Leave both sources unchanged.

- [ ] **Release any stopped cloud-sync process through the fail-safe cleanup and verify process identity before backup.**

- [ ] **Restore automatic network time after the verdict and successful backups.** Record restoration time and confirm the state is on.

- [ ] **Run exact-basis governed extraction.** Use an absolute runs root, the frozen extraction spec, the passing evaluation-basis SHA-256, and bundle hashing:

  ```sh
  .venv/bin/python scripts/extract_detection_floors.py \
    --runs-root "$RUNS_ROOT" \
    --spec "$WINDOW_PLAN_ROOT/extraction_spec.json" \
    --out "$CUSTODY_ROOT/window-c-extraction.json" \
    --evaluation-basis-sha256 "$WHOLE_WINDOW_BASIS_SHA256" \
    --hash-bundles
  ```

- [ ] **Require extraction exit 0 and exact membership.** Require `all_cells_extractable: true`, no specification-membership or idle-admission refusal, matching drift allowances, no fallback-anchor or mock member, and an explicit disposition for every planned occurrence.

- [ ] **Keep extraction and consuming analysis in the same lead-controlled custody session while the standalone-floor binding limitation remains open.**

- [ ] **Complete the close-out record.** Include code/policy/plan hashes; window times; supply identity; every calibration attempt; bound members and freshness; seven references; both allowances; verdict basis; failure/quarantine/supersession inventory; both backup results; extraction result; clock disable/restore times; and counts by distinct bundle ID.

If any required result fails, preserve all evidence and report the strongest lower status earned. Do not call the window claim-bearing.

### Desk analysis and required C-iv figures

Every figure must identify the physical Mac, OS version/build, runtime and library versions, model artifact hash, quantization, tokenizer, sampler and output policy, configured and realized batch/concurrency, measurement boundary, and telemetry backend.

| Figure | Exact output |
|---|---|
| **Linearity** | Observed output count versus gross request energy and decode energy; fitted slopes and intervals; residual panel; tested range clearly limited to 128–2048 tokens. |
| **Null ladder** | ABBA delta and interval at each short/mid/long magnitude; zero line and the matching decision envelope; state whether false contrasts remain contained as magnitude grows. |
| **Empirical floor** | Predicted floor multiple versus observed signed delta and interval for every frozen level and both directions; label each result `refused`, `resolved`, or `failed expected behavior`. |
| **Additivity** | Prefill-plus-decode versus enclosing request energy with identity line; residual/setup/gap accounting by shape. |
| **Causal invariance** | Prefill energy versus later output length at fixed prompt length; slope and frozen equivalence/acceptance band. A nonzero result narrows the phase claim. |
| **Drift and settling** | Start/mid/end reference trajectory with published allowance; long-hold and post-transition thermal/admission recovery against the 180-second convention. Show midpoint curvature rather than reporting endpoints alone. |
| **Between-session stability** | At least three identity-matched sessions/days showing calibration bounds, repeated null blocks, and repeated floor cells. State whether the declared freshness/reuse rule holds or each session needs a new floor. |

## Known failure modes and their preventive checks

| Prior failure | Exact prevention before launch | If it appears |
|---|---|---|
| **Screensaver/display contamination** | Run `quiet_mac_prep.sh`; require explicit all-displays-asleep and screensaver-disengaged evidence; retain `--arm-quiet-mode --arm-countdown-s 20` on every stage; prove the awake/saver negative tests still refuse. | Lose the occurrence, preserve it, remove the cause, and follow only the frozen recovery. Never override admission. |
| **Clock-anchor failure** | Verify the wall clock first; disable network time; settle 180 seconds; require the 5 ms gate; freeze zero member-level anchor retries and one calibration-only clock retry. | Preserve and quarantine a failed member and stop the stage. Do not hand-retry it. |
| **Environment-admission binding failure** | Fresh roots; exact campaign manifests and log; arm-time preflight on every invocation; valid before/after observations; negative test for missing or temporally invalid evidence. | Refuse the occurrence or entire basis as machinery directs. Never replace authenticated binding with a directory scan. |
| **Out-of-family pre calibration** | Drain idle maintenance; verify quiet state; use the issued level screen before member 1; freeze the cause-removal retry count. | Abort before science. Retry only after naming and removing a cause; never rerun until lucky. |
| **140 W charger negotiating 70 W** | Re-probe negotiated voltage/current/wattage immediately before launch and bind it in the readiness record. | NO-GO. Repair cable/port/supply state outside the window. |
| **Agent or terminal output during idle admission** | Close Claude, Codex, t3, browsers, watchers, and tails; independent census; one-line arm message; no streaming afterward. | Treat the affected occurrence as contaminated. |
| **Idle maintenance starts after launch** | At least ten untouched minutes plus consecutive clean pre-window checks before the chain. | Preserve the refusal; wait for the named process to finish; follow only the frozen recovery. |
| **Outcome-driven calibration retry** | Freeze retry counts and reasons; retain every attempt; chain screens the pre calibration automatically. | End the attempt when no named removable cause exists. |
| **Membership or verdict shopping** | Freeze exact members and comparisons; one ordinary verdict; explicit passing-basis SHA in extraction. | Stop on any conflict. Never append a semantically different verdict over the same basis. |

## Provenance appendix

- Collection procedure, physical preparation, custody, ABBA, verdict, backup, and extraction: `docs/phase_2/window_runbook.md`.
- Fresh-claim reset, no-Window-B rule, readiness preconditions, and hard start fence: `docs/decision_log.md`, D-113 clauses 7–9.
- Frozen metrology campaign vocabulary and four frozen plans: `docs/decision_log.md`, D-096.
- Calibration screens, drift limits, and acceptance-artifact chain: D-079, D-102, D-109, and `configs/calibration/calibration_acceptance_d079_v2.json`.
- Window failure history and zero-streaming rule: D-098/D-099 and `docs/run_reports/2026-08-01-metrology-window-b.md`.
- Third-failure closure: D-087.
- Current Window C task and start dependencies: `TASK_QUEUE.md` and `/tasks/MET-WINDOW-C-01` in `docs/process/state_kernel.json`.
- A+ characterization outputs: `docs/paper/draft-v1.md` §6 and `docs/phase_2/detection_floor.md`.

exec
/bin/zsh -lc "sed -n '1,224p' docs/phase_2/window_runbook.md && sed -n '225,453p' docs/phase_2/window_runbook.md && sed -n '454,683p' docs/phase_2/window_runbook.md" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
# Quiet-Mac Claim-Window Run-Book

**Operator:** Ed

**Lane:** `[QUIET-MAC]`

**Applies to:** claim-bearing Mac measurement windows after PR #85

**Main authorities:** D-077, D-078, and D-079 in `docs/decision_log.md`,
`docs/phase_2/detection_floor.md`,
`configs/campaign_policies/quiet_mac_p2_production.json`, and
`configs/campaigns/window_references/README.md`

This is the practical procedure for collecting one claim window. A **claim
window** is one uninterrupted measurement session whose members share one
power state, one instrument identity, one fresh NEG-8 drift bound, and one
whole-window verdict. A **member** is one run bundle. A **reference** is the
fixed `df_rq_mid` workload used to detect and budget drift. A **drift
allowance** is the nonzero uncertainty term that a passing window adds to
every floor or claim in the matching energy family.

Do not run this procedure while any agent session is active. The operator
owns the quiet machine from the first calibration through the post
calibration.

## 1. Rules that do not bend

- [ ] Start from reviewed, merged `main` with a clean measurement checkout.
- [ ] Close Claude, Codex, browser automation, periodic monitors, and every
  process that would wake or poll the machine.
- [ ] Launch one foreground shell chain and wait for its one completion
  event. Do not inspect logs while it runs.
- [ ] Keep the approved charger, cable, wattage, and power policy unchanged.
- [ ] Do not touch the keyboard, trackpad, lid, display controls, power
  settings, charger, or cable during the chain.
- [ ] Keep every display asleep and the screensaver disengaged throughout
  each campaign invocation. An awake display is a measurement contaminant,
  not an operator convenience.
- [ ] Use transient display sleep only. Do not change persistent display or
  screensaver preferences as part of a window.
- [ ] Settle for 150–240 seconds after operator activity, stage churn, a
  calibration retry, or a failed attempt. Use 180 seconds unless the frozen
  plan says otherwise.
- [ ] Preserve every failed, incomplete, or aborted artifact. Never delete or
  overwrite evidence to make a window pass.
- [ ] Quarantine an occupied retry slot outside the runs root, recollect the
  exact member, and record the old occurrence with
  `--record-supersession`.
- [ ] Do not waive environment admission, calibration, clock, thermal,
  adapter-continuity, anchor-fallback, mock-telemetry, or drift-allowance
  failures.
- [ ] Back up the immutable corpus before extraction.
- [ ] Until FLOOR-BIND-01 closes, honour registered limitation L1: a
  claim-bearing analysis may consume a floor artifact only when that artifact
  was produced by the governed extraction in the same lead-controlled custody
  session as **the analysis**. L1 binds extraction to analysis, not collection
  to extraction — collection may happen in an earlier session — but extraction
  and the analysis that consumes its floors may never be split.

The practical target is one compact 2–4 hour window. If the work will not fit,
split it into another independently calibrated window. A long window is not
more rigorous: the a5 collection showed that a delayed end reference can be
physically stale.

## 2. The post-PR #85 compatibility gate is satisfied

Merged main now provides all of the surfaces that the earlier draft was
waiting for:

- **Per-family screens and allowances.** The whole-window verdict evaluates
  `gross_energy` and `idle_subtracted_energy` separately. Each family gets
  its own derived repeatability bound and its own recorded drift allowance:
  `max(observed start/midpoint/end excursion, derived bound)`. Passing never
  turns the allowance into zero.
- **Reference triplet protocol.** The governed prospective references are
  under `configs/campaigns/window_references/`: three start members, one
  midpoint member, and three end members. The endpoint means and standard
  errors feed the screens; the midpoint catches an interior excursion.
- **Bound freshness.** The governed dual-family
  `joulewise.neg8_drift_bound.v1` artifact has a fixed 24-hour
  (`86400 s`) horizon and exact OS-build, power-supply-identity, and
  calibration-identity bindings. Expiry, an identity change, or unresolved
  bindings refuse with `neg8_drift_bound_stale`.
- **Anchor-fallback member gate.** A fallback-clock-anchored member cannot
  supply a floor or claim cell. For floor-campaign roles it is an unwaivable
  rerun trigger, reported as `anchor_fallback_member_unusable`.

Therefore a new claim window may proceed. Do not fall back to the old
single-start/single-end practice for new collection.

Before freezing the plan, confirm the command surface:

```sh
.venv/bin/python scripts/run_campaign.py --help
```

The required options are `--arm-quiet-mode`, `--arm-countdown-s`,
`--log`, `--instrument-calibration-dir`, `--instrument-power-policy`,
`--derive-neg8-drift-bound`, `--neg8-drift-bound-output`,
`--whole-window-verdict`, and `--neg8-drift-bound`.

### Decision on the three flags missing from the draft chain

The merged CLI accepts all three. They are deliberately included in every
measurement-campaign invocation in this run-book:

- `--arm-quiet-mode` counts down, calls `pmset displaysleepnow`, and then
  performs the complete governed environment re-probe. It is the merged
  enforcement surface for the display/screen-contamination lesson.
- `--arm-countdown-s 20` is not syntactically required; the CLI default is
  5 seconds. The proven `claim_windows.sh` used 20 seconds, and this run-book
  keeps that operator margin so Ed can step away before display sleep and
  re-probe.
- `--log "$RUNS_ROOT/campaign_log.jsonl"` is also not syntactically required
  because the same path is the default. It remains explicit so collection,
  supersession, verdict, and later consumers all name the same custody log.

The verdict and bound-mint modes do not measure a member, so they receive
`--log` where applicable but not the display-arm flags.

## 3. Time budget in plain language

Budget these pieces before selecting campaign stages:

| Operation | Expected time |
|---|---:|
| Stage settle | 180 seconds |
| Display arm inside each campaign | 20-second countdown plus re-probe |
| Protocol-v3 calibration | about 4 minutes; the commanded schedule alone is 196.7 seconds |
| NEG-8 bound corpus | 12 ordinary reference members plus one 180-second settle |
| Start references | 3 ordinary reference members plus one settle/arm |
| Midpoint reference | 1 ordinary reference member plus one settle/arm |
| End references | 3 ordinary reference members plus one settle/arm |
| Failure margin | at least 20% of the planned window |

Use the dry run and prior measured member durations to budget the ordinary
members. Do not estimate them from model size alone. If the reference corpus,
two calibrations, seven window references, chosen science stages, settles,
and failure margin do not fit in the window, remove science stages before
arming.

The 24-hour freshness horizon is a ceiling, not permission to reuse
yesterday's bound. For this procedure, the 12-member bound corpus must be
collected and the bound must be minted **inside the same quiet window that
uses it**, before the start triplet. This keeps the OS, supply, and
calibration identity aligned and makes the bound causal for that window.

## 4. Freeze the plan before quiet time

Create one plan directory outside the runs roots:

```text
WINDOW_PLAN_ROOT/
├── window.env
├── before_midpoint_stages.txt
├── after_midpoint_stages.txt
├── extraction_spec.json
├── waivers.json
└── window-chain.zsh
```

Each stage-list line is one repository-relative config directory, for
example:

```text
configs/campaigns/p2_015_floors/04_phase_prefill_abba
configs/campaigns/p2_015_floors/03_request_abba
```

Do not put the reference directories in those lists; the chain adds the
governed 3+1+3 references itself.

Example `window.env`:

```sh
WINDOW_ID=window_a9_YYYYMMDD
RUNS_ROOT=/Users/edr/code/JouleWise/runs_window_a9_YYYYMMDD
BOUND_RUNS_ROOT=/Users/edr/code/JouleWise/runs_window_a9_YYYYMMDD_bound
CUSTODY_ROOT=/Users/edr/JouleWise-window-custody/window_a9_YYYYMMDD
BACKUP_DEST="/Users/edr/Library/Mobile Documents/com~apple~CloudDocs/JouleWise-backup/window_a9_YYYYMMDD"
POWER_POLICY=ac_high_power
SETTLE_S=180
```

`RUNS_ROOT` holds the claim-window members and calibration bracket.
`BOUND_RUNS_ROOT` holds only the 12-member settled-reference corpus used to
mint this window's bound. Keep the roots separate so the corpus members do
not accidentally enter the claim-window member basis.

Before quiet time:

- [ ] Give every planned bundle one unique run ID.
- [ ] Freeze membership and stage order before looking at outcomes.
- [ ] Create `waivers.json` containing `[]`.
- [ ] Keep quarantine, operator logs, extraction output, and the plan outside
  both runs roots.
- [ ] Validate every config.
- [ ] Dry-run every stage against its intended root.
- [ ] Resolve every doctor warning; do not add `--ack-config-warnings`
  casually.
- [ ] Record `git rev-parse HEAD`.

Useful checks:

```sh
git status --short --branch
git rev-parse HEAD

.venv/bin/python -m joulewise doctor --campaign --json \
  configs/campaigns/neg8_reference_corpus/neg8-refcorpus-*.json \
  configs/campaigns/window_references/start_triplet/neg8-window-start-*.json \
  configs/campaigns/window_references/midpoint/neg8-window-midpoint.json \
  configs/campaigns/window_references/end_triplet/neg8-window-end-*.json

.venv/bin/python scripts/run_campaign.py \
  configs/campaigns/window_references/start_triplet \
  --runs-dir "$RUNS_ROOT" \
  --campaign-policy configs/campaign_policies/quiet_mac_p2_production.json \
  --dry-run
```

Repeat the dry run for the bound corpus, midpoint, end triplet, and every
science stage. Dry-run mode does not write campaign-log entries.

## 5. Machine and operator preflight

- [ ] Connect the approved charger and cable. Record wattage and
  `POWER_POLICY`.
- [ ] Finish or pause Time Machine, software updates, indexing churn, large
  downloads, and cloud uploads.
- [ ] Confirm `sudo -n powermetrics` succeeds.
- [ ] Perform the pre-window clock stabilization in §5A. It needs
  administrator rights, so only Ed can do it and the chain cannot.
- [ ] Let idle-triggered background daemons run **before** the window, not
  inside it. macOS starts idle-only work — XProtect's scheduled malware scan
  is the documented instance — in roughly the first 10 minutes after the
  machine goes quiet. Leave the machine untouched and idle for at least 10
  minutes before launching the chain. This is in addition to the 180-second
  stage settle, not satisfied by it.
- [ ] Confirm the chain carries the §5B pre-flight calibration screen and
  that the frozen plan records the pre-registered retry bound (D-079
  clause 3).
- [ ] Confirm both fresh runs roots do not already contain member bundles.
- [ ] Confirm the backup destination exists and has enough free space.
- [ ] Close every agent and browser-automation session.
- [ ] Explain the single rule to anyone nearby: do not touch the Mac until
  the chain announces completion.

Run the preparation probe once, read its result, and correct any failure
before closing the final terminal:

```sh
bash scripts/quiet_mac_prep.sh
```

That script uses transient display sleep and does not change persistent
display or screensaver settings. The campaign still arms and re-probes on
every invocation; the preparation script is not a certificate for later
members.

An idle-triggered daemon that fires inside the window contaminates the member
it lands on and will fail CPU admission. That is the gate working, not a false
alarm: window a9's first bound-corpus member was lost exactly this way and was
correctly caught. The response is always preserve, quarantine, supersede, then
relaunch (§10). It is never a waiver and never `--environment-override`.

## 5A. Pre-window clock stabilization (administrator step; Ed performs it)

**This is operational stabilization, not a protocol waiver.** The 5 ms
wall-versus-monotonic anchor ceiling stays exactly where it is. It is never
relaxed, widened, or waived, and a member that trips it is still lost. The
steps below reduce how often the machine trips it. They do not change what
trips it.

### What went wrong, in plain language

Every measured member must be anchored causally in time. The anchor check
compares two clocks: the **wall clock**, which is the machine's idea of the
current date and time and which network time synchronisation adjusts, and the
**monotonic clock**, a counter that only ever counts forward and is never
adjusted. The difference between them must stay within `5 ms`
(`MAX_WALL_MINUS_MONOTONIC_SPAN_S`, `joulewise/uncertainty_evidence.py:22`)
across a member's clock stamps. When it does not, the predicate at
`joulewise/uncertainty_evidence.py:367` refuses the member with the detail
string `wall_minus_monotonic_span_exceeded`.

Two consecutive window-C collection attempts on 2026-07-26 failed on exactly
that, and on nothing else:

| Attempt | Member that failed | Observed span | Implied rate |
|---|---|---:|---:|
| 1 | `p2015-df-cmp-abba-ph-decode-b02-b2` | 5.544 ms | about +110 ppm |
| 2 | `neg8-refcorpus-r11` | 7.769 ms | about −158 ppm |

Rates of that size are what `adjtime(2)` produces. `adjtime(2)` is the system
call network time synchronisation uses to correct the wall clock by speeding
it up or slowing it down by a fraction of a percent, instead of jumping it, so
that time keeps increasing. The evidence shows a **slew** — a gradual change
of rate — and not a demonstrated discrete step: no timestamp ever moved
backward, and the native powermetrics second counter advanced only by 0 or 1
whole seconds. A step hidden inside the roughly 44-second gap between stamps
cannot be categorically excluded.

Two things are unknown and must be written as unknown wherever this is
reported:

- **The responsible process is unknown.** `joulewise/environment.py:908`
  assigns `clock_sync.status = "limited_without_admin"` unconditionally, and
  the `timed_running` field only reports whether `pgrep` found the process.
  Every member, passing and failing alike, reported `timed_running=true`. The
  macOS `timed` daemon is therefore **plausible but unproven**; attributing it
  would require privileged inspection of the unified log.
- **The correlation with time of day is noted but unproven.** Window B had
  zero occurrences across 59 members, collected 23:57–03:15 local. Window C
  ran roughly 7% per member — 2 occurrences across about 30 members, collected
  03:17–05:19 local. Do not assert a nightly maintenance-window cause.

What is established: only a privileged wall-clock adjuster can produce this.
Ordinary sampling load, thermal state, and CPU activity cannot move the wall
clock relative to the monotonic clock. The excursion also self-clears — member
`neg8-refcorpus-r12`, collected immediately after the failing `r11`, anchored
cleanly with a 0.305 ms span.

### Before the window (administrator rights required)

macOS gates both the read and the write of this setting behind administrator
rights (`systemsetup -getusingnetworktime` and
`systemsetup -setusingnetworktime`), so the chain script can neither perform
nor verify this step. Ed performs it by hand.

- [ ] **Confirm the system clock is actually correct first.** Disabling
  automatic time on a wrong clock freezes that error in place for the whole
  window. Compare the system clock against an independent trusted source and
  correct it before going further.
- [ ] Record the current setting so it can be restored:

  ```sh
  sudo systemsetup -getusingnetworktime
  ```

- [ ] Disable automatic network time adjustment:

  ```sh
  sudo systemsetup -setusingnetworktime off
  ```

- [ ] Settle 150–240 seconds — use 180 — after this administrator action, as
  after any other operator activity, before launching the chain.
- [ ] After the window closes, meaning after `measurement_complete`, the
  whole-window verdict, and the backup, re-enable it:

  ```sh
  sudo systemsetup -setusingnetworktime on
  ```

- [ ] Record in the close-out that automatic time was disabled, when it was
  disabled, and when it was restored.

Leaving automatic time off is not a protocol state. It is a temporary machine
condition the operator owns for one window, and the close-out must show it was
returned.

### If a single member still fails the anchor

Stabilization lowers the rate; it does not make the failure impossible. When
one member refuses with `wall_minus_monotonic_span_exceeded`, no member-level
anchor retry is adopted. Under D-113 clause 9, no such retry occurs without a
prospective ruling made before the plan freeze:

- [ ] **Do not mint a bound, a verdict, or a floor from a basis that contains
  the invalid occurrence.** An invalid member never becomes a valid one.
- [ ] Preserve and quarantine the invalid member. Valid members already
  collected stay exactly where they are, but no replacement member is
  collected under an unruled retry.
- [ ] Stop the stage under the existing `--max-failures 1` behavior and take
  the disposition to the lead. Do not hand-retry, supersede, or rerun the
  dual-family bound mint as if a member-level retry were licensed.

`--max-failures` stays at 1. Every admission gate, every family screen, and
every refusal stays exactly as written. Calibration-only retry remains
governed as written in §6 and is not changed by this member-level prohibition.

## 5B. Pre-flight calibration screen (D-079 clause 3)

**What this catches, in plain language.** The pre-calibration measures how
badly the power instrument can be wrong about *when* energy was used. It
reduces to one number, the fiducial bound (`b_fiducial_s` in
`instrument_evidence.json`). Most captures land near 27 ms. Occasionally the
GPU is still ramping its clock and voltage up through low-frequency states
while the calibration pulses run — the raw evidence shows the GPU is not
idle — and the estimator, which fits each pulse as a clean rectangle with a
movable start time, absorbs that ramp as an apparent shift in the pulse's
start. The result is an out-of-family calibration. Window B on 2026-07-26 hit
exactly this: a 35.435841 ms pre-calibration, the highest in the entire
corpus, which was only discovered at the post-calibration and cost the whole
3.5-hour campaign. The condition cannot be predicted before a calibration is
taken, but a four-minute calibration detects it reliably. That asymmetry is
the entire point of this step.

**The screen.** Immediately after the pre-calibration mints, and before any
member is collected:

1. Read `b_fiducial_s` from the newly minted
   `RUNS_ROOT/instrument_validation/<id>/instrument_evidence.json`.
2. Require `b_fiducial_s <= 0.033558756679900` (33.558756680 ms). This is the
   larger, and so the more conservative, of the prior observed maximum
   (33.558756680 ms) and the 95% Student-t upper level for a new observation
   over the same n=19 corpus (33.353749299 ms).
3. If the value exceeds the threshold, **abort before member 1** and go to
   the retry rules below. Do not proceed and hope the post-calibration
   agrees; it will not save the window, and every member collected after a
   failing pre-calibration is wasted quiet time.
4. If the value passes, continue the chain unchanged.

The chain in §6 performs steps 1–3 automatically, so the operator still never
inspects logs mid-run. The threshold is a derived, provenance-bound number,
not a house style: it is valid only for Mac15,9 / macOS 25F84 /
`ac_high_power` / 100 ms cadence / `joint_loss_sublevel_interval_branch_v2`
bindings, and it is re-derived when any of those change (D-079 clause 3).

This screen is a **level** check on one calibration, and is entirely separate
from the **drift** check between the two calibrations in §8. A level failure
is an out-of-family systematic condition and is never budgeted (D-079
clause 2).

**Retry rules — the cause-removal test.**

- A failing pre-calibration ends **that attempt**, not necessarily the night.
- A retry is permitted **only** when a specific, named cause has been
  identified **and removed**. Record the retry as a deviation in the
  close-out, preserve both attempts as immutable evidence, and stay inside
  the retry count pre-registered in the frozen plan.
- **With no identifiable cause, the window ends.** Stop, preserve everything,
  and take the disposition to the lead.
- The line that matters: re-running until the number passes is selection on
  the **outcome**. That is calibration shopping, it makes the accepted
  calibration the luckiest draw rather than a representative one, and it
  would invalidate every claim built on the window. Re-running after removing
  a named **cause** is legitimate, because the second attempt measures a
  genuinely different machine state.
- Worked example (2026-07-27, window C): Apple's XProtect malware scanner was
  observed at 94% CPU as the window's first member began. The environment
  gate refused the member — correctly. The scanner was identified as the
  cause, the operator waited 14 minutes for it to finish, and the relaunched
  window collected 59/59 clean. Named cause, removed, verified, recorded:
  that is a legitimate retry. "It failed, so I ran it again" is not.

D-079 defines this screen on the pre-calibration only. If the **post**
calibration's level exceeds the same threshold, the members are already
collected and no retry can help: preserve everything, record it in the
close-out, do not budget the excess (D-079 clause 2), and refer the
disposition to the lead.

## 6. The foreground measurement chain

Save the following as `WINDOW_PLAN_ROOT/window-chain.zsh`, review it, and
record its SHA-256 before closing all agents:

```zsh
#!/bin/zsh
set -euo pipefail

WINDOW_PLAN_ROOT="$1"
source "$WINDOW_PLAN_ROOT/window.env"

REPO=/Users/edr/code/JouleWise
PY="$REPO/.venv/bin/python"
POLICY="$REPO/configs/campaign_policies/quiet_mac_p2_production.json"
REF_ROOT="$REPO/configs/campaigns/window_references"
BOUND_CONFIG_ROOT="$REPO/configs/campaigns/neg8_reference_corpus"
BOUND_MANIFEST="$BOUND_CONFIG_ROOT/derivation/settled_corpus.json"
CLAIM_LOG="$RUNS_ROOT/campaign_log.jsonl"
BOUND_LOG="$BOUND_RUNS_ROOT/campaign_log.jsonl"
NEG8_DRIFT_BOUND="$BOUND_RUNS_ROOT/neg8-drift-bound.json"
OPERATOR_LOG_ROOT="$CUSTODY_ROOT/operator_logs"
QUARANTINE_ROOT="$CUSTODY_ROOT/quarantine"

mkdir -p \
  "$RUNS_ROOT/instrument_validation" \
  "$BOUND_RUNS_ROOT" \
  "$OPERATOR_LOG_ROOT" \
  "$QUARANTINE_ROOT"

timestamp() {
  TZ=UTC date '+%Y-%m-%dT%H:%M:%SZ'
}

settle() {
  /bin/sleep "$SETTLE_S"
}

quarantine_stale_lock() {
  local root="$1"
  local lock="$root/campaign.lock"
  [ ! -e "$lock" ] && return 0

  local pid
  pid="$(/usr/bin/sed -n 's/^pid=\([0-9][0-9]*\).*/\1/p' "$lock")"
  if [ -z "$pid" ]; then
    echo "Unreadable campaign lock: $lock" >&2
    return 1
  fi
  if /bin/kill -0 "$pid" 2>/dev/null; then
    echo "Live campaign PID $pid owns $lock" >&2
    return 1
  fi

  /bin/mv "$lock" \
    "$QUARANTINE_ROOT/$(basename "$root").campaign.lock.$(TZ=UTC date '+%Y%m%dT%H%M%SZ')"
}

latest_calibration() {
  /usr/bin/find "$RUNS_ROOT/instrument_validation" \
    -mindepth 1 -maxdepth 1 -type d -print |
    /usr/bin/sort |
    /usr/bin/tail -n 1
}

arm_for_calibration() {
  echo "$(timestamp) calibration display arm: 20-second countdown" \
    >> "$OPERATOR_LOG_ROOT/window-chain.log"
  /bin/sleep 20
  /usr/bin/pmset displaysleepnow \
    >> "$OPERATOR_LOG_ROOT/window-chain.log" 2>&1
  /bin/sleep 5
}

calibrate_once() {
  local label="$1"
  arm_for_calibration
  "$PY" "$REPO/scripts/validate_powermetrics_fiducial.py" \
    --allow-live \
    --output-root "$RUNS_ROOT/instrument_validation" \
    --power-policy "$POWER_POLICY" \
    >> "$OPERATOR_LOG_ROOT/${label}-calibration.log" 2>&1
}

calibrate_with_clock_retry() {
  local label="$1"
  local before candidate rc reasons

  settle
  before="$(latest_calibration)"
  set +e
  calibrate_once "$label"
  rc=$?
  set -e
  candidate="$(latest_calibration)"

  if [ "$rc" -eq 0 ] && [ -n "$candidate" ] && [ "$candidate" != "$before" ]; then
    print -r -- "$candidate"
    return 0
  fi

  [ -n "$candidate" ] || return 1
  reasons="$(/usr/bin/jq -r '.reasons[]?' \
    "$candidate/instrument_evidence.json" | /usr/bin/sort -u)"
  if [ "$reasons" != "clock_anchor_unresolved" ]; then
    echo "$label calibration failed: $reasons" >&2
    return 1
  fi

  settle
  before="$candidate"
  set +e
  calibrate_once "${label}-retry"
  rc=$?
  set -e
  candidate="$(latest_calibration)"
  [ "$rc" -eq 0 ] && [ -n "$candidate" ] && [ "$candidate" != "$before" ] || return 1
  print -r -- "$candidate"
}

# D-079 clause 3: pre-flight calibration screen. Refuses an out-of-family
# pre-calibration before any member is collected. Threshold is bindings-bound
# (Mac15,9 / macOS 25F84 / ac_high_power / 100 ms / estimator v2); see §5B.
PRE_CAL_FIDUCIAL_MAX_S=0.033558756679900

screen_pre_calibration() {
  local dir="$1"
  local b

  b="$(/usr/bin/jq -r '.b_fiducial_s // empty' \
    "$dir/instrument_evidence.json")"
  if [ -z "$b" ]; then
    echo "pre-calibration has no fiducial bound: $dir" >&2
    return 1
  fi
  echo "$(timestamp) pre_calibration_fiducial_s=$b" \
    >> "$OPERATOR_LOG_ROOT/window-chain.log"
  if (( b > PRE_CAL_FIDUCIAL_MAX_S )); then
    echo "pre-calibration fiducial $b exceeds D-079 screen $PRE_CAL_FIDUCIAL_MAX_S" >&2
    echo "$(timestamp) pre_calibration_screen=failed" \
      >> "$OPERATOR_LOG_ROOT/window-chain.log"
    return 1
  fi
  echo "$(timestamp) pre_calibration_screen=passed" \
    >> "$OPERATOR_LOG_ROOT/window-chain.log"
}

run_stage() {
  local root="$1"
  local log="$2"
  local config_dir="$3"
  local calibration_dir="$4"
  local label="$5"

  settle
  quarantine_stale_lock "$root"
  echo "$(timestamp) stage_start=$label" >> "$OPERATOR_LOG_ROOT/window-chain.log"

  "$PY" "$REPO/scripts/run_campaign.py" "$config_dir" \
    --runs-dir "$root" \
    --log "$log" \
    --campaign-policy "$POLICY" \
    --instrument-calibration-dir "$calibration_dir" \
    --instrument-power-policy "$POWER_POLICY" \
    --arm-quiet-mode \
    --arm-countdown-s 20 \
    --max-failures 1

  echo "$(timestamp) stage_end=$label" >> "$OPERATOR_LOG_ROOT/window-chain.log"
}

run_stage_list() {
  local list="$1"
  local stage
  while IFS= read -r stage; do
    [ -z "$stage" ] && continue
    [[ "$stage" = \#* ]] && continue
    run_stage "$RUNS_ROOT" "$CLAIM_LOG" "$REPO/$stage" "$PRE_CAL_DIR" "$stage"
  done < "$list"
}

cd "$REPO"
echo "$(timestamp) chain_start" >> "$OPERATOR_LOG_ROOT/window-chain.log"

PRE_CAL_DIR="$(calibrate_with_clock_retry pre)"
echo "$(timestamp) pre_calibration=$PRE_CAL_DIR" >> "$OPERATOR_LOG_ROOT/window-chain.log"

# Abort before member 1 if the pre-calibration is out of family (§5B).
screen_pre_calibration "$PRE_CAL_DIR"

# The reference corpus and bound are minted inside this same quiet window.
run_stage "$BOUND_RUNS_ROOT" "$BOUND_LOG" "$BOUND_CONFIG_ROOT" "$PRE_CAL_DIR" \
  neg8-bound-corpus

"$PY" "$REPO/scripts/run_campaign.py" \
  --derive-neg8-drift-bound "$BOUND_MANIFEST" \
  --neg8-drift-bound-output "$NEG8_DRIFT_BOUND" \
  --runs-dir "$BOUND_RUNS_ROOT" \
  >> "$OPERATOR_LOG_ROOT/bound-mint.log" 2>&1
echo "$(timestamp) neg8_bound=$NEG8_DRIFT_BOUND" >> "$OPERATOR_LOG_ROOT/window-chain.log"

run_stage "$RUNS_ROOT" "$CLAIM_LOG" "$REF_ROOT/start_triplet" "$PRE_CAL_DIR" \
  start-reference-triplet

run_stage_list "$WINDOW_PLAN_ROOT/before_midpoint_stages.txt"

run_stage "$RUNS_ROOT" "$CLAIM_LOG" "$REF_ROOT/midpoint" "$PRE_CAL_DIR" \
  midpoint-reference

run_stage_list "$WINDOW_PLAN_ROOT/after_midpoint_stages.txt"

run_stage "$RUNS_ROOT" "$CLAIM_LOG" "$REF_ROOT/end_triplet" "$PRE_CAL_DIR" \
  end-reference-triplet

POST_CAL_DIR="$(calibrate_with_clock_retry post)"
echo "$(timestamp) post_calibration=$POST_CAL_DIR" >> "$OPERATOR_LOG_ROOT/window-chain.log"
echo "$(timestamp) measurement_complete" >> "$OPERATOR_LOG_ROOT/window-chain.log"
```

After every agent is closed, launch exactly once:

```sh
caffeinate -is /bin/zsh "$WINDOW_PLAN_ROOT/window-chain.zsh" "$WINDOW_PLAN_ROOT"
```

Expected visible behavior: each stage pauses for the 180-second settle, prints
a 20-second arming countdown, sleeps the display, re-probes the governed
environment, and then begins members. The two calibrations use their own
20-second transient display arm. Do not wake the display to check progress.


exec
/bin/zsh -lc "sed -n '684,1009p' docs/phase_2/window_runbook.md" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
## 7. Display and screen governance

The production policy requires AC power, an externally connected source,
low-power mode off, all online displays asleep, the screensaver disengaged,
and Nominal thermal pressure.

`--arm-quiet-mode` is intentionally repeated for every campaign invocation.
It is not redundant: every invocation gets a new enforcing preflight after
the previous stage's process churn. The controller also records governed
environment evidence and observes the display after capture. If the display
wakes or the screensaver engages, the correct outcome is refusal or loss of
the affected member.

Do not work around an environment failure with `--environment-override`.
That option records an override and makes every resulting member universally
claim-ineligible.

## 8. Check the fresh bound and calibration bracket

After `measurement_complete`, wake the display once.

- [ ] Confirm the pre and post artifacts are valid protocol v3.
- [ ] Confirm pre is at or before the first claim member and post is at or
  after the last.
- [ ] Confirm both are under
  `RUNS_ROOT/instrument_validation/`.
- [ ] Confirm both are within 24 hours and share the same power-policy and
  instrument bindings.
- [ ] Confirm bracket-bound drift against the **derived** screen of
  `0.010818 s` (10.817749309 ms), not the old underived `0.010 s`
  constant (D-079 clause 1). Drift within the screen passes clean.
- [ ] If drift is slightly above the screen, the window is **not**
  discarded: the excess becomes an added uncertainty term carried into
  every floor and claim the window produces, so the floor publishes wider.
  Do not compute or apply that allowance by hand — the governed verdict and
  extraction own it, exactly as they own the NEG-8 drift allowances.
- [ ] Confirm the excess being budgeted is ordinary repeatability scatter and
  **not** a known systematic defect (D-079 clause 2). A budget may never
  absorb a measurement already known to be wrong for an identified reason;
  that would launder the defect into a respectable-looking interval. In
  particular, a pre-calibration that failed the §5B level screen is never
  budgetable, and its window is not claim-bearing — window B (2026-07-26,
  drift 11.581436 ms on a 35.435841 ms pre-calibration) is the standing
  example, and `instrument_calibration_mismatch` is the correct verdict for
  it.
- [ ] Confirm the bound artifact was minted during this window from all 12
  members in `BOUND_RUNS_ROOT`.
- [ ] Confirm the bound freshness block says `max_age_s: 86400` and matches
  the claim members' OS build, supply identity, and calibration identity.

Do not hand-calculate or patch a family bound or allowance. The governed
verdict computes both family screens and both allowances.

## 9. Emit exactly one whole-window verdict

Run the verdict only after the post calibration and fresh bound are ready:

```sh
.venv/bin/python scripts/run_campaign.py \
  --whole-window-verdict \
  --runs-dir "$RUNS_ROOT" \
  --log "$RUNS_ROOT/campaign_log.jsonl" \
  --campaign-policy configs/campaign_policies/quiet_mac_p2_production.json \
  --neg8-drift-bound "$BOUND_RUNS_ROOT/neg8-drift-bound.json"
```

Add `--waivers "$WINDOW_PLAN_ROOT/waivers.json"` only when the frozen basis
contains a waiver that the current contract permits. A waiver makes the
whole-window verdict `flagged`; claim-bearing extraction requires `passed`.

- [ ] Require `status: passed`.
- [ ] Record `evaluation_basis.sha256`, the exact member-occurrence set, the
  calibration bracket, and policy SHA-256.
- [ ] Require both `gross_energy` and `idle_subtracted_energy` screens to
  pass.
- [ ] Require both authenticated entries under `drift_allowances`.
- [ ] Confirm every member's CPU admission is `admitted`.
- [ ] Confirm adapter wattage continuity is `stable`.
- [ ] Treat the gross corner statistic as diagnostic, not gating.
- [ ] Do not append a semantically different verdict for the same basis.

A passing screen is not a declaration of zero drift. The allowance is the
budget carried into every matching floor or claim envelope.

### D-100 §9 amendment — explicit salvage-dangler verdict dispatch

The ordinary command above never consumes a terminally absent member and
never selects a salvage row. A D-100 re-evaluation is a separate, licensed
operation performed only after an audited `joulewise.salvage_closure.v1` and
an exhaustive `joulewise.whole_window_membership_binding.v1` have been
lead-verified. It appends one new row; it does not edit a failed row:

```sh
.venv/bin/python scripts/run_campaign.py \
  --whole-window-verdict \
  --runs-dir "$RUNS_ROOT" \
  --log "$RUNS_ROOT/campaign_log.jsonl" \
  --campaign-policy configs/campaign_policies/quiet_mac_p2_production.json \
  --neg8-drift-bound "$BOUND_RUNS_ROOT/neg8-drift-bound.json" \
  --consumption-semantics-id salvage_dangler_exclusion_v1 \
  --window-membership-binding "$WINDOW_PLAN_ROOT/window-membership-binding.json" \
  --salvage-closure "$CUSTODY_ROOT/salvage-closure.json"
```

The new basis consumes every surviving member under authenticated
max-bracket re-derivation plus exactly one D-100 exclusion. Every downstream
consumer must name both `salvage_dangler_exclusion_v1` and that row's exact
64-hex `evaluation_basis.sha256`. `--waivers` is forbidden in this mode.
Creating the artifacts or running this command does not itself license a
historical window; that remains a separate lead-controlled step.

## 10. Failure playbook

| Symptom or refusal | Meaning | Required action |
|---|---|---|
| Display awake, screensaver engaged, `environment_admission_failed`, or CPU admission failure | The measurement environment was contaminated or unknown. | Lose the affected member. Stop the stage, remove the cause, settle 180 seconds, and rerun into a clean slot. Never waive admission. |
| `clock_anchor_unresolved` on calibration | The calibration capture could not be causally anchored. | Preserve it, settle, and retry once into a new validation directory. Abort after the second failure or any different calibration reason. |
| `pulse_calibration_rollover_gate_timeout` | Native powermetrics time did not advance before the pulse train. | Abort calibration and preserve the evidence. Repair machine state outside the window. |
| Pre-calibration fiducial above `0.033558756679900` (chain aborts before member 1) | The pre-calibration is out of family — typically a GPU clock/voltage ramp aliased into the fitted pulse start (D-079 clause 3). | Do not collect. Retry only after naming and removing a specific cause, within the pre-registered retry count, recording both attempts as evidence (§5B). With no identifiable cause, end the window. Never re-run merely to obtain a passing number. |
| Bracket drift above `0.010818 s` (D-079 derived screen) | Either ordinary repeatability scatter slightly over the screen, or an out-of-family systematic. | If the pre-calibration passed the §5B level screen, the window survives: the excess is carried by the governed extraction as an added uncertainty term and floors publish wider. If the §5B level screen failed, the excess is not budgetable and the window is not claim-bearing (D-079 clause 2). Never hand-apply an allowance. |
| `instrument_calibration_bracket_missing` | The claim members lack a valid causal pre/post calibration pair. | Mark the window non-claim-bearing. Never borrow a calibration from another power or machine state. |
| `calibration_bracket_exceeds_minted_bound` | The post calibration's bound is larger than one or more member envelopes minted under the pre calibration. | Do not patch metadata. Re-reduce only through a governed prospective path; otherwise recollect. |
| `neg8_drift_bound_underived` or `neg8_idle_sub_drift_bound_underived` | One family has no authenticated derived bound. | Collect the complete settled-reference corpus and mint the dual-family artifact. Never insert a constant or borrow the other family. |
| `neg8_drift_bound_stale` | The 24-hour horizon expired, a bound identity changed, or current bindings are missing/conflicting. | Mint a new corpus and bound inside the quiet window that will use it. |
| `neg8_bracket_abs_delta_exceeded` or `neg8_bracket_idle_sub_abs_delta_exceeded` | The gross or idle-subtracted point-drift screen failed. | Reject this claim basis. Preserve it and collect a shorter or better-controlled new window. |
| `anchor_fallback_member_unusable` in a floor cell | A floor member used unresolved or fallback clock anchoring. | This is an unwaivable rerun trigger. Preserve the fragment, quarantine the occupied slot, rerun the exact member, and record supersession. |
| `bundle_strict_invalid` from telemetry identity | The custody-bound config, metadata adapter, and summary telemetry source disagree by backend class. | Stop. Do not choose the convenient label. Repair custody or recollect the bundle. |
| `mock_telemetry_claim_ineligible` | A custody-bound config identifies mock telemetry. | Terminally refuse the member for claims. Mock data is development evidence and has no claim waiver. |
| `whole_window_drift_allowance_unrecorded` | A passing basis lacks an authenticated family allowance, or a claim omitted its named allowance term. | Refuse the affected floor/claim. Never substitute zero; rerun the governed verdict/extraction path or recollect if provenance cannot be restored. |
| `whole_window_campaign_membership_unresolved` | Campaign-log provenance is missing, ambiguous, duplicated, or unbound. | Repair custody or recollect. Do not replace manifest evidence with a directory scan. |
| `whole_window_verdict_conflict` | Different stored verdict rows purport to govern one basis, or verdict history is malformed. | Stop. Latest-wins is forbidden; preserve the conflict and mint a genuinely new basis if needed. |
| `incomplete_existing` or an occupied run ID | A failed or interrupted bundle already owns the path. | Strict-validate and preserve it, move it outside the runs root, rerun the exact config, then record supersession. |
| `another campaign appears to be running` | A live process or stale `campaign.lock` owns the root. | Check the PID. Stop for a live PID. Move a dead lock to quarantine; never delete an unreadable lock blindly. |
| Operator touches display, input, lid, or power | The governed state changed during the window. | Lose the active member. If supply identity changed, end the entire window and start a new root with new calibrations and a new bound. |

An anchor-fallback member may be excluded by governed extraction rules when
membership still satisfies policy, but for a planned floor-campaign member
the operator response is still recollection. Never accept a fallback member
as a zero-width floor.

### Slot quarantine and supersession

Inspect the occupied bundle:

```sh
.venv/bin/python -m joulewise validate-bundle --strict \
  "$RUNS_ROOT/$BUNDLE_ID"
```

Move it outside the runs root:

```sh
mv "$RUNS_ROOT/$BUNDLE_ID" \
  "$QUARANTINE_ROOT/${BUNDLE_ID}__$(TZ=UTC date '+%Y%m%dT%H%M%SZ')"
```

After the exact replacement exists and is strict-valid, record the old
occurrence:

```sh
.venv/bin/python scripts/run_campaign.py \
  --record-supersession "$BUNDLE_ID" \
  --quarantine-path "$QUARANTINED_BUNDLE_PATH" \
  --reason "Aborted occupied slot; old occurrence preserved and strict-valid replacement selected" \
  --runs-dir "$RUNS_ROOT" \
  --log "$RUNS_ROOT/campaign_log.jsonl" \
  --campaign-policy configs/campaign_policies/quiet_mac_p2_production.json
```

Two present bundles for one occurrence always refuse.

### D-100 §10 amendment — terminally absent salvage is exceptional

Zero present bundles is `terminal_absent`, not a successful retry. It refuses
by default. The only non-refusing disposition is capped at one absent member
and requires three same-failure D-087 occurrences bound by byte-derived
signatures and exhaustive evidence. Each occurrence must mechanically prove
one of these branches:

- a hash-bound launcher refusal with no bytes for the member anywhere in the
  closure-declared custody universe (the runs root plus every declared
  quarantine/custody root); or
- a pre-workload admission abort whose only `stage_started` prefix is
  `validate`, `prepare`, `idle_baseline`, whose metadata records
  `environment_admission.decision: abort`, a nonempty ordered attempt list
  with every `admitted: false`, and
  `claim_reason: environment_admission_failed`, and whose failed summary has
  every measurand field null.

For the second branch, powermetrics/rich telemetry may end at most **0.250 s**
after the idle-baseline failure event. The observed 136–171 ms final flush is
teardown evidence; a later sample, a missing or truncated event stream, any
workload/measurement stage, any non-null measurand, an unknown non-null
summary field, an unreadable file, a symlink/duplicate artifact, or a fourth
occurrence voids the license. Preserve original failed bundles and verdict
rows byte-for-byte.

### Post-calibration failure and the a10 recorded deviation

The chain retries a calibration exactly once, and only when the sole reason is
`clock_anchor_unresolved` (`calibrate_with_clock_retry`, §6). Any other
calibration reason aborts, as the table above requires.

Window a10 recorded an operator deviation against that rule. Its first post
calibration, `20260725T055825`, failed with pulse-detection reasons rather
than `clock_anchor_unresolved`; the frozen run-book said abort and repair the
machine outside the window. The lead instead settled and retried, and the
retry, `20260725T060617`, was valid. Both captures are preserved.

What kept that deviation from corrupting the record is the discipline that
still binds every operator here:

- [ ] Preserve every failed calibration attempt under
  `RUNS_ROOT/instrument_validation/`. Never delete or overwrite one.
- [ ] Consume the **earliest valid causal post calibration**. Never select
  among valid captures on the basis of the bound each one produces. In a10 no
  such selection occurred, and that is why the retry was recoverable.
- [ ] Record any retry, its reason, and both directory names in the close-out
  as a deviation.

Whether a post-calibration retry is permitted for a non-clock failure is not
settled by this run-book. Until Ed rules (§13.2), the standing instruction
remains abort and repair outside the window, and any retry is a recorded
deviation rather than a licensed step.

## 11. Back up, then extract in the same custody session

Back up the claim corpus:

```sh
bash scripts/backup_runs.sh "$RUNS_ROOT" "$BACKUP_DEST"
```

Require exit code 0 and keep the source root unchanged.

Then run governed extraction:

```sh
.venv/bin/python scripts/extract_detection_floors.py \
  --runs-root "$RUNS_ROOT" \
  --spec "$WINDOW_PLAN_ROOT/extraction_spec.json" \
  --out "$CUSTODY_ROOT/detection-floor-extraction.json" \
  --evaluation-basis-sha256 "$WHOLE_WINDOW_BASIS_SHA256" \
  --hash-bundles
```

- [ ] Require exit code 0 and `all_cells_extractable: true`.
- [ ] Require no `spec_membership_refusals` or
  `idle_admission_refusals`.
- [ ] Confirm extraction consumes the exact passing whole-window basis.
- [ ] Confirm each floor cell carries the matching
  `whole_window_drift_allowance`.
- [ ] Confirm no anchor-fallback or mock member entered a claim-bearing cell.
- [ ] Confirm custody-bound config, metadata, and summary telemetry identities
  agree.
- [ ] Confirm every campaign member is included, superseded, quarantined, or
  explicitly refused.
- [ ] Keep extraction output outside immutable bundle directories.

The allowance widens the already guarded/corner-widened floor. It does not
replace instrument uncertainty, and it is never silently omitted.

## 12. Close-out record

Record:

- the exact Git commit and policy hash;
- the window ID, start/end times, and power-supply identity;
- pre/post calibration IDs, bounds, and bracket drift;
- the 12 bound-corpus bundle IDs, bound derivation SHA-256, mint time, expiry,
  and freshness bindings;
- all seven window-reference bundle IDs, endpoint means and standard errors,
  midpoint value, both family screen results, and both allowances;
- the whole-window evaluation-basis SHA-256 and member occurrence set;
- every failed, quarantined, superseded, or waived occurrence;
- backup destination and exit status;
- extraction artifact path and result;
- whether automatic network time was disabled for this window, when it was
  disabled, and when it was restored (§5A);
- every calibration attempt, including failed ones, and any retry recorded as
  a deviation;
- member counts by distinct bundle ID, never by campaign-log line.

Call the window **claim-bearing** only when the whole-window verdict is
`passed`, both family allowances are authenticated, the backup succeeds, and
same-custody extraction completes with no refusal. Otherwise preserve the
evidence and report the strongest lower, non-claim-bearing status it actually
earned.

## 13. Open questions for Ed (recorded, not adopted)

Nothing in this section is in force. Do not act on any of it during a window.
It is recorded here so the argument is not lost between sessions.

### 13.1 A governed member-level retry for `clock_anchor_unresolved`

**Observation.** `calibrate_with_clock_retry` (§6) already treats
`clock_anchor_unresolved` as the one retryable condition **for calibrations**,
retrying once after a settle. There is no equivalent retry for **members**. A
single member that hits the same transient clock condition fails that member,
and under `--max-failures 1` that one failure aborts the whole stage.

**For.** The condition is demonstrably transient and self-clearing: in §5A,
`neg8-refcorpus-r11` failed at a 7.769 ms span and `r12`, collected
immediately after it, anchored cleanly at 0.305 ms. A governed member-level
retry — once only, after a full settle, restricted to
`clock_anchor_unresolved` alone, with the failed occurrence quarantined and
superseded exactly as today — would have saved both lost windows.

**Against.** Any retry loosens the fail-closed posture. A systematic clock
problem would present as a run of individually retried transients, and the
retry would mask it: the window would look healthy while producing members
collected under a drifting clock. The current behaviour makes the problem
loud, which is the only reason it was diagnosed at all.

This is a protocol change affecting claim-bearing data, so it is explicitly
Ed's call. Do not implement it, and do not treat a hand retry as an
equivalent.

### 13.2 Post-calibration retry shape for a non-clock failure

Raised by the window-a10 deviation recorded in §10, "Post-calibration failure
and the a10 recorded deviation". The question is whether a post calibration
that fails for a reason other than `clock_anchor_unresolved` may be retried
once after a settle, or must abort the window as the current text requires.
Undecided; the current text stands.

codex
The operating chain is clear: Ed must own the Mac in person through the physical/sudo arm, then the machine is entirely unattended until `measurement_complete`. I’m now separating the shared chain from the three science payloads so each night remains a true one-page checklist with unresolved plan values visibly marked.
exec
/bin/zsh -lc "sed -n '1,382p' docs/phase_2/splitwise_decode_campaign.md && sed -n '383,557p' docs/phase_2/splitwise_decode_campaign.md" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
# Splitwise-vein decode contrast campaign (splitwise_decode_v1) — FROZEN PLAN DRAFT

**STATUS: DRAFT FROZEN PLAN + DRAFT PRE-REGISTRATION. NOT RATIFIED.**
**The magistrate ratifies; the lieutenant delivers. Do not run a window from this
document until §10 Q1 is answered.**

Authored 2026-07-29 for a quiet window the same night. Supersedes the 2026-07-29
WIP checkpoint (commit `3a73b03` + the M4 line in `3de370e`); the checkpoint's
evidence base is carried forward and re-verified below, its unmeasured 7B timing
estimate is replaced by a measured probe, and its central assumption — that the
contrast can be gated against the minted decode floor — is **refuted** in §2.

The task (Ed-directed, 24 h deadline) is the project's first cross-model
comparative campaign: decode-phase energy, Qwen2.5-1.5B-Instruct-4bit (arm A) vs
Qwen2.5-7B-Instruct-4bit (arm B), one quiet window under
`configs/campaign_policies/quiet_mac_p2_production.json`.

## 1. What is authored and where

| Deliverable | Location | State |
|---|---|---|
| Cross-model contrast campaign | `configs/campaigns/splitwise_decode_v1/` | authored, validator-clean |
| 7B decode floor calibration (contingency) | `configs/campaigns/qwen25_7b_decode_floor_v1/` | authored, validator-clean |
| 7B model profile | §3 below | finalized |
| Duration arithmetic | §4 below | measured-probe-based |
| Pre-registration sheet | §5 below | DRAFT, conditional on §2 |
| Operator checklist delta | §6 below | draft |
| Validation record | §7 below | lead-run |
| Open questions | §10 below | for ratification |

Both campaigns follow the `configs/campaigns/p2_015_floors/` convention: a
deterministic `generate_configs.py` that writes only below its own directory,
freezes one `calibration_plan.json` before any measurement, hashes the exact plan
bytes into `calibration_plan.sha256` and into every member config's
`calibration-plan-sha256=` tag, and emits one `order_manifest.json` per stage plus
a root manifest. Neither campaign directory contains the window references or the
NEG-8 bound corpus: `docs/phase_2/window_runbook.md` §4 forbids listing those as
science stages, because `window-chain.zsh` supplies the governed 3+1+3 references
(`configs/campaigns/window_references/`) and the 12-member in-window bound corpus
(`configs/campaigns/neg8_reference_corpus/`) itself, on the unchanged 1.5B
`df_rq_mid` condition.

## 2. BLOCKING FINDING — the contrast is collectible tonight but not claimable

Verified this session by direct reading of the primary code, not by report.
**Two independent blockers stand between tonight's contrast bundles and a gated
claim.** Neither is a defect; both are the ratified P2-039/D-058 design working as
designed. Both were unknown when the checkpoint was written.

### Blocker A — the 7B arm has no floor, and floor transport is stack-bound

`floor_stack_identity` (`joulewise/analysis_engine/inputs.py:426-513`) derives the
stack identity from *realized bundle evidence*, and one of its eleven components is

```python
"model_artifact_sha256": artifact_sha,
```

taken from `workload_provenance.model.artifact_identity`. A 7B bundle therefore has
a different `stack_identity_sha256` from every 1.5B bundle, necessarily.

Every route from a consumer to a floor is gated on that hash:

- Evidence homogeneity: all evidence rows for one condition family must yield
  exactly one stack hash, else no floor request is built at all
  (`inputs.py:2862-2871`, `if len(consumer_stack_hashes) != 1: return None`).
- Exact-cell match additionally requires
  `binding.cell_stack_identity_sha256.get(cell_id) != consumer_stack_hash → continue`
  (`inputs.py:2884-2894`).
- Transport match requires `("stack_identity_sha256", consumer_stack_hash)` to
  equal the transport group's (`inputs.py:2912-2921`).

The minted artifact `df-ph-decode-floor-mint1` carries exactly one cell and one
transport group, both bound to the **1.5B** calibration stack, and exactly one
allowed consumer condition family — `df-ph-decode` with hash `e38e2a2f…762bfe`
(`scripts/mint_floor_artifact.py:1514-1528`, ids hard-pinned at `:59-93`).

Consequence: **the 7B arm resolves no floor under any naming.** The refusal is
`floor_row_missing` / `floor_transport_inapplicable`, both in `_NOT_RESOLVABLE`
(`joulewise/analysis_engine/claims.py:170,173`), and one unusable arm voids the
contrast — `if not all_usable: floor_abs = floor_cmp = floor_gate = None`
(`joulewise/analysis_engine/__init__.py:405-408`).

Arm A does not clear either, for a second reason worth recording. If arm A declares
the family id `df-ph-decode`, `same_condition_seen` is set (`inputs.py:2878-2881`)
and the exact-cell match then fails on `cell_scientific_identity_sha256` — a new
campaign's members carry different run-metadata tags from window C's, and
`scientific_config_identity` (`inputs.py:1846-1866`) strips only `run_id`, `rep\d+`,
the two `analysis-replacement-*` tags, and the four `calibration-*` prefixes. Once
`same_condition_seen` is true, transport is not attempted at all
(`inputs.py:2908-2909`, `if matches or same_condition_seen: return None`). If arm A
instead declares a new family id, transport *is* attempted but
`allowed_consumer_condition_families` lists only `df-ph-decode`, so no group
matches.

The prerequisite for any 7B decode claim is therefore a **7B decode floor**:
absolute + null-ABBA calibration on the 7B stack, extracted and minted. That is what
`configs/campaigns/qwen25_7b_decode_floor_v1/` collects. Note that consumption of
that evidence also needs tooling work: `scripts/mint_floor_artifact.py` is
hard-pinned to the p2_015 / a10 / window-C evidence (`CELL_ID`, `PLAN_SHA256`,
both order-manifest ids, `A10_SPEC_MEMBERS = 30`, `WINDOW_C_SPEC_MEMBERS = 40`,
`EXPECTED_OPERATIVE_FLOOR_TEXT = "7.377086"`) and needs a generalized sibling. That
work is desk work; the collection is not.

### Blocker B — no analysis-manifest schema can express a model-vs-model contrast

`analyze_claims` validates its manifest with the AP-2 **v1** validator
unconditionally (`inputs.py:403`, importing `validate_analysis_manifest` from
`joulewise.analysis_manifest` at `inputs.py:22`). That validator is frozen to the
Slice-2M speculation design:

- `contrast["block_ids"]` must equal `[f"block-2m-{model_tag}-r{rep:02d}" …]`
  derived by stripping `cell-2m-` / `cond-2m-` prefixes
  (`joulewise/analysis_manifest.py:1347-1356`);
- `multiplicity` must equal `{"method": "holm", "alpha": 0.05, "q": None, "m": 6}`
  (`analysis_manifest.py:1391`);
- estimator must be `paired_block_mean_difference_t_v1`, direction `two_sided`,
  `equivalence` and `mde` both null.

The v2 sibling (`joulewise/analysis_engine/registry.py:390`) is equally frozen —
`floor["condition_family_ids"] == ["spec_off", "spec_on"]` — and is not the
validator `analyze_claims` uses.

Consequence: **even with two floors in hand, no manifest for a
Qwen2.5-1.5B-vs-7B decode contrast validates on this branch.** Extending the
manifest vocabulary is design-bearing, contract-adjacent work — not a tonight task.

### What this does and does not mean

It does **not** mean the campaign is wrong or the evidence is worthless. Bundles
collected under a frozen, pre-registered plan in a governed quiet window remain
valid evidence; what is missing is the consumption path. It **does** mean the
document's original framing — "the first claim-bearing comparative campaign …
consumed into claims against the operative decode floor" — is not achievable from
tonight's window, and the pre-registration in §5 is conditional.

### Option set for the magistrate (§10 Q1)

| | Option | Runs tonight | Estimated window | What it buys | What it still needs |
|---|---|---|---|---|---|
| **O1** | Floor-first | `qwen25_7b_decode_floor_v1` | ~3.0 h | The 7B decode floor evidence — the strict prerequisite for every 7B claim | A generalized mint tool (desk work) |
| **O2** | Contrast-as-evidence | `splitwise_decode_v1` | ~2.6 h | The contrast bundles banked under a frozen plan | The 7B floor *and* new manifest machinery, both unbuilt |
| **O3** | Both, two independently calibrated windows | both | ~5.6 h + two brackets | Everything | Ed's availability; runbook §3 prefers splitting over one long window |
| **O4** | Defer collection | neither | — | A night of mint-generalization and manifest-extension design | Another quiet window later |

**Lieutenant's advisory recommendation: O1.** It is the only option whose collected
evidence has a fully specified consumption route (existing extraction + a
generalized mint, no new science), it is on the critical path for *both* O2 and any
later cross-generation work, and it spends the scarce resource — a quiet window on
a machine that must otherwise sit idle — on the one thing that cannot be done at a
desk. Under O1, `splitwise_decode_v1` stays authored and ratified-in-principle for
the next window. The decision is the magistrate's; both campaigns are runnable
tonight either way.

## 3. Model artifact status — FINALIZED

`mlx-community/Qwen2.5-7B-Instruct-4bit` is **present and complete** on the
measurement machine (verified 2026-07-29 by direct listing, not by report):

- Local directory: `/Users/edr/jw_models/mlx-community/Qwen2.5-7B-Instruct-4bit`
- `model.safetensors` 4,284,346,255 bytes; `model.safetensors.index.json` present;
  tokenizer, vocab, merges, config all present. Directory total 4.0 GB.
- **Revision pin: `c26a38f6a37d0a51b4e9a1eb3026530fa35d9fed`** (HF hub `refs/main`,
  resolved at download time 2026-07-29 ~16:30 PT).
- `weight_format`: `mlx`; `family`: `qwen2.5`; `context_window`: 32768.

Arm A is unchanged from window C: `Qwen2.5-1.5B-Instruct-4bit`, revision
`8b403126fc14f14cfc99bb4cfa72ecbc129ea677`, source
`/Users/edr/jw_models/mlx-community/Qwen2.5-1.5B-Instruct-4bit`.

Two-model load pattern and its consequences:

- A stage is one `run_campaign.py <stage_dir>` invocation, and within a contrast
  stage arms alternate every member, so each member incurs a model load. The
  timing figures in §4 are per-member wall times that already include it.
- The **first in-window 7B load reads ~4 GB from NVMe cold**. It lands inside the
  first B member of the first contrast stage (or of stage `01_phase_decode_absolute`
  under O1). It is inside the member's own settle/warmup structure and is not a
  contamination source, but it is the largest single-member time outlier to expect.
- No network access is required or permitted during the window; the snapshot is
  local and revision-pinned. There is no tooling that verifies the snapshot before
  launch — see the §6 preflight addition.

Disk: **113 GB free** on `/System/Volumes/Data` (verified `df -g`, 2026-07-29).
`WINDOW_STATUS.md`'s "13 GB free" line is stale and should be corrected at
bookkeeping; `RUN_STATE.md`'s 115 GB figure is the current one. Both far exceed the
20 GB threshold in `scripts/prewindow_check.sh:115-123`. The window-C and a10 runs
roots must not be pruned to make room — they are mint #1 inputs.

## 4. Duration arithmetic — measured probe, not model-size inference

`docs/phase_2/window_runbook.md:136-140` forbids estimating member duration from
model size, which is exactly what the checkpoint's ~120-130 s figure did. It is
replaced here by a timing probe run 2026-07-29 outside any window:

| Quantity | Value | Source |
|---|---:|---|
| 1.5B `df_ph_decode` member wall time | 92.7 s | measured, n=40, `runs_window_c_20260726/campaign_log.jsonl` |
| 1.5B `df_rq_mid` reference member | 90.5 s | measured, n=7, same log |
| 1.5B generation time (512 tok) | 2.05 s | probe, 2026-07-29 |
| 7B generation time (512 tok) | 6.40 s | probe, 2026-07-29 |
| **7B `df_ph_decode` member wall time** | **~97 s** | probe + 92.7 s anchor |

The member is overwhelmingly fixed overhead (180 s stage settle amortized, 30 s
idle, 5 s warmup seconds, arm/settle, sampling teardown); the model-dependent term
is warmup + measured generation, and the probe puts the 7B penalty at ~4.35 s per
pass rather than the ~11-15 s the size-based guess assumed.

### O2 — contrast window (`splitwise_decode_v1`, 40 members: 20 A + 20 B)

| Piece | Est. minutes |
|---|---:|
| Pre-calibration (180 s settle + 20 s arm + ~4 min protocol-v3) | ~8 |
| NEG-8 bound corpus, 12 x 90.5 s + settle/arm | ~22 |
| Bound mint | ~1 |
| Start reference triplet, 3 x 90.5 s + settle/arm | ~8 |
| Science stage 1 — blocks 1-5 (10 A x 92.7 s + 10 B x 97 s) + settle/arm | ~35 |
| Midpoint reference, 1 x 90.5 s + settle/arm | ~5 |
| Science stage 2 — blocks 6-10 + settle/arm | ~35 |
| End reference triplet + settle/arm | ~8 |
| Post-calibration | ~8 |
| **Subtotal** | **~130** |
| +20% failure margin (runbook §3) | **~156 min (~2.6 h)** |

### O1 — 7B floor window (`qwen25_7b_decode_floor_v1`, 50 members, all 7B)

| Piece | Est. minutes |
|---|---:|
| Pre-calibration | ~8 |
| NEG-8 bound corpus + settle/arm | ~22 |
| Bound mint | ~1 |
| Start reference triplet | ~8 |
| Stage 01 — absolute, 10 x 97 s + settle/arm | ~20 |
| Stage 02 — null-ABBA blocks 1-5, 20 x 97 s + settle/arm | ~36 |
| Midpoint reference | ~5 |
| Stage 03 — null-ABBA blocks 6-10, 20 x 97 s + settle/arm | ~36 |
| End reference triplet | ~8 |
| Post-calibration | ~8 |
| **Subtotal** | **~152** |
| +20% failure margin | **~182 min (~3.0 h)** |

Sensitivity: if the 7B member is actually 130 s (the checkpoint's discarded upper
guess, +34%), O2 becomes ~169 min (~2.8 h) and O1 ~215 min (~3.6 h). Both remain
inside a 4 h window; O1 has less headroom and is the one to watch. Neither needs an
`n_blocks` reduction. Both are inside the runbook's 2-4 h compact-window target;
O3 is not, which is why it is written as two windows.

## 5. Pre-registration sheet — DRAFT, CONDITIONAL on §2

Recorded now, before any measurement, so that it is pre-registered whichever option
runs. **Conditional**: the decision-interval clause below cannot be evaluated until
the §2 blockers are cleared, and the contrast is therefore registered as
*evidence-bearing now, claim-bearing later*, never as an exploratory contrast
promoted after the fact.

### 5.1 `splitwise_decode_v1` — cross-model decode contrast

- **Directional expectation, stated before data:** decode-phase energy per request
  is **greater** for Qwen2.5-7B-Instruct-4bit than for Qwen2.5-1.5B-Instruct-4bit
  on the identical `df_ph_decode` workload (128 prompt / 512 output tokens).
  Physical basis: 4-bit weights of ~4.0 GB vs ~0.9 GB on a memory-bandwidth-bound
  unified-memory device, at identical token counts.
- **Estimand:** the paired per-block mean difference `B - A` of
  `phase_energy_j.decode`, `difference_orientation:
  condition_b_minus_condition_a`, over 10 blocks.
- **Design:** 10 contiguous A/B/B/A blocks, 40 members, fixed label order, no RNG
  (existing project convention; see §10 Q5). Blocks 1-5 run before the midpoint
  reference and blocks 6-10 after, so the interior reference genuinely divides the
  science — a change from window C, which ran all 40 members in one stage.
- **`minimum_claim_n`: 10 blocks.** A window that collects fewer than 10 valid
  blocks yields no claim; it does not yield a claim at reduced n.
- **Acceptance clause (conditional):** a directional claim is admissible only if
  its decision interval clears the operative decode floor **and** the per-claim
  claim-side anchor bound. Per the D-078 clause 11 ruling of 2026-07-29, these are
  **two gates, not one sum**: the operative floor is the cell gate, the claim-side
  `E_clock_anchor_shift_bound_j` is separately consumed by the claim's decision
  interval, and the additive expression `floor_j + claim_side_bound_j` is a
  **disclosure obligation** that must be stated wherever an attribution-limited
  floor is published — never an acceptance threshold and never a double count.
  For the 1.5B stack the operative floor is **7.377086 J** (cell gate,
  comparative-dominant; absolute component 3.592138 J), artifact
  `df-ph-decode-floor-mint1`. **For the 7B stack no floor exists yet** (§2
  Blocker A); the 7B arm's gate value is unknown and must be minted before this
  clause can be evaluated.
- **Replacement rule:** `technical_invalid_same_slot_only`, pre-declared before
  data, `outcome_dependent_top_up: forbidden_and_demotes_contrast_to_exploratory`.
  A member may be replaced only in its own slot and only for a technical
  invalidity established without looking at its energy value.
- **No outcome-contingent selection anywhere:** no member, block, arm, or stage may
  be added, dropped, reordered, or re-run on the basis of an observed effect;
  no post-hoc block exclusion; no top-up to reach significance.
- **Refusal conditions (any one refuses the claim, not just the member):** whole-window
  verdict not PASSED; calibration bracket drift outside
  `calibration_bracket_max_drift_s = 0.01`; NEG-8 in-window bound not minted inside
  this window before the start triplet; fewer than 10 valid blocks; any arm whose
  members do not share a single scientific config identity and a single stack
  identity; any floor unresolvable for either arm; any evidence-root mapping that is
  not exact (§6).

### 5.2 `qwen25_7b_decode_floor_v1` — 7B decode floor calibration

- **Purpose:** establish the detection floor for `phase_energy_j.decode` on the
  Qwen2.5-7B-Instruct-4bit stack. This is a calibration, not a claim; it registers
  no directional expectation.
- **Design:** one absolute cell (10 repeats) and one comparative null-ABBA cell
  (10 blocks / 40 members), both on the single condition family
  `df-ph-decode-qwen25-7b`, whose definition is byte-identical to
  `configs/floor_mint/condition_family_df_ph_decode.json` apart from the id — same
  workload profile, same measurement target, same two frozen literals.
- **`minimum_claim_n`: 10**, matching the 1.5B floor and exceeding the
  `GUARD_MINIMUM_N = 5` in `joulewise/detection_floor.py:2230-2233`.
- **Same replacement rule and the same no-outcome-contingent-selection clause** as
  §5.1.
- **Known downstream gap, registered now:** the existing mint tool cannot consume
  this evidence without generalization (§2 Blocker A, closing paragraph). The
  evidence is collected against that known gap deliberately, because the collection
  requires a quiet window and the generalization does not.

## 6. Operator checklist delta vs `docs/phase_2/window_runbook.md`

The runbook is unchanged and remains authoritative. These are **additions and
corrections for this campaign only**; none of them relaxes an existing gate.

**D-1. Add the disk/readiness preflight to §5.** `scripts/prewindow_check.sh`
exists and blocks below 20 GB free (`:115-123`), but the runbook never references
it — §5's only free-space language is an eyeball check on the *backup* destination.
Run it before the plan freeze:

```sh
bash scripts/prewindow_check.sh --window <label>
```

Current state: 113 GB free, well clear. Do not prune `runs_window_c_20260726*` or
`runs_window_a10_20260725*` to make room; they are mint #1 inputs.

**D-2. New — two-model snapshot preflight (there is no tooling for this).** Before
the plan freeze, confirm by hand that both model snapshots are present, complete,
and revision-correct, because the window forbids network access and a missing
snapshot fails mid-stage:

```sh
ls -la /Users/edr/jw_models/mlx-community/Qwen2.5-1.5B-Instruct-4bit
ls -la /Users/edr/jw_models/mlx-community/Qwen2.5-7B-Instruct-4bit
```

Expect `model.safetensors` at 4,284,346,255 bytes in the 7B directory. Confirm the
revision recorded in §3 matches what the member configs pin. Under O1 every member
is 7B; under O2 both snapshots are load-bearing.

**D-3. New — cold-load expectation.** The first 7B member of the window reads ~4 GB
from NVMe cold. Expect that member's wall time to exceed the ~97 s estimate. It is
not a failure signal on its own; the 20% margin absorbs it. Do not intervene.

**D-4. Timing figures for the budget (replaces the runbook's "do not estimate from
model size" gap with measured input).** Use 92.7 s per 1.5B `df_ph_decode` member,
90.5 s per `df_rq_mid` reference member, and **97 s per 7B `df_ph_decode` member**
(probe-derived, §4). Do not re-derive from parameter counts.

**D-5. Standing — exact evidence-root mappings.** On every claim run, pass exactly
one `--evidence-root ID=PATH` per artifact-declared evidence root and **no surplus
entries**. This holds regardless of FIX-8's status. Surplus entries have twice been
a refusal source (binder exact-cover, then output-separation), and an exact mapping
is the shape both the binders and the separation check agree on.

**D-6. Stage lists.** Under O2, `before_midpoint_stages.txt` contains exactly
`configs/campaigns/splitwise_decode_v1/01_decode_contrast_blocks_01_05` and
`after_midpoint_stages.txt` exactly
`configs/campaigns/splitwise_decode_v1/02_decode_contrast_blocks_06_10`. Under O1,
`before_midpoint_stages.txt` contains
`configs/campaigns/qwen25_7b_decode_floor_v1/01_phase_decode_absolute` then
`configs/campaigns/qwen25_7b_decode_floor_v1/02_phase_decode_abba_blocks_01_05`,
and `after_midpoint_stages.txt` contains
`configs/campaigns/qwen25_7b_decode_floor_v1/03_phase_decode_abba_blocks_06_10`.
Never list a reference or bound-corpus directory (runbook §4).

**D-7. Unchanged, stated for completeness.** §5A clock stabilization, the §5B
pre-calibration fiducial screen (`b_fiducial_s <= 0.033558756679900`), the 3+1+3
governed references, the 12-member in-window bound corpus and its same-window mint,
the `quiet_mac_p2_production` policy binding via `--campaign-policy`, `--max-failures 1`,
and the single `caffeinate -is /bin/zsh …/window-chain.zsh` launch all apply
unmodified.

## 7. Validation record (lead-run, 2026-07-29)

All gates run by the lead in the `impl/mint-tool` worktree with
`/Users/edr/code/JouleWise/.venv/bin/python` (this worktree has no `.venv` of its
own — use the measurement checkout's pinned interpreter for the pre-window rerun).

**G-1 `joulewise doctor --campaign --json`, per stage, member configs only.**

| Stage | n | `config` | verdict |
|---|---:|---|---|
| `splitwise_decode_v1/01_decode_contrast_blocks_01_05` | 20 | pass | warn |
| `splitwise_decode_v1/02_decode_contrast_blocks_06_10` | 20 | pass | warn |
| `qwen25_7b_decode_floor_v1/01_phase_decode_absolute` | 10 | pass | warn |
| `qwen25_7b_decode_floor_v1/02_phase_decode_abba_blocks_01_05` | 20 | pass | warn |
| `qwen25_7b_decode_floor_v1/03_phase_decode_abba_blocks_06_10` | 20 | pass | warn |

Zero config errors and zero unacknowledged config warnings on every stage. The
`warn` verdict comes only from `backup_destination` (not configured in a desk
session) and `quiet_machine` (hard-coded `warn` at `joulewise/doctor.py:551`; agent
sessions were open). `powermetrics` passed. Both warns are expected outside a
window and neither is a config property.

**Glob caveat, worth recording for the operator:** a stage `*.json` glob includes
`order_manifest.json`, which doctor tries to parse as a `BenchmarkConfig` and
rejects — producing a spurious `config: fail`. `run_campaign.py` *requires* that
sidecar in the stage directory, so the two tools disagree about the glob, not about
the configs. Always pass member-only globs to doctor.

**G-2 `scripts/run_campaign.py <stage> --dry-run`** (with `--runs-dir` on a scratch
root and `--campaign-policy configs/campaign_policies/quiet_mac_p2_production.json`):
rc=0 on all five stages, emitting 20/20/10/20/20 `dry_run` lines respectively —
matching each stage's member count, in manifest order, first block confirmed as
`b01-a1 → b01-b1 → b01-b2 → b01-a2`. The order-manifest exact-cover and
index-contiguity checks inside `apply_order_manifest` are part of this gate and
passed.

**G-3 `git diff --check`**: clean, rc=0.

**G-4 Per-arm scientific config identity (the constraint that decides usability).**
Computed independently by the lead with
`joulewise.analysis_engine.inputs.scientific_config_identity`:

| Campaign | Arm / family | members | distinct identities |
|---|---|---:|---:|
| `splitwise_decode_v1` | `sw-decode-a-qwen25-1p5b` | 20 | **1** |
| `splitwise_decode_v1` | `sw-decode-b-qwen25-7b` | 20 | **1** |
| `qwen25_7b_decode_floor_v1` | `df-ph-decode-qwen25-7b` | 50 | **1** |

One identity per arm is required — more than one makes the arm unresolvable
(`inputs.py:2851-2857`).

**G-5 Frozen-plan integrity.** Each `calibration_plan.sha256` matches the SHA-256 of
the exact plan bytes, and every member config's `calibration-plan-sha256=` tag
matches its campaign's plan hash (0 mismatches across all 90 members):

- `splitwise_decode_v1`: `7b563724be38254bf0769bca5818e9bcd70f76288e79650b55c3e051bf636b04`
- `qwen25_7b_decode_floor_v1`: `62f7ab3b981ea81f280ee770e932858025b74758bb3dfa5b684bffcbe6a3b388`

**G-6 Condition-family definitions** all return `[]` from
`validate_condition_family_definition`. Domain hashes
(`joulewise.condition_family.v1`), which will appear in any future artifact key:

- `sw-decode-a-qwen25-1p5b`: `c13a3ebf5461ed9a442a8e67555f70301848d56a55ab766570d46ca067934f12`
- `sw-decode-b-qwen25-7b`: `5149a8552600341883439a73fa135caa0e6ba292544c7c6fe2e69674318df4e3`
- `df-ph-decode-qwen25-7b`: `a20018d57f06d69ffcc1…` (full value in the definition's
  consuming spec when one is written)

**G-7 Determinism.** Both generators re-run; the aggregate hash over all 108 files
was byte-identical before and after.

**G-8 Structure.** Root manifests carry 40 and 50 contiguous entries; every ABBA
block in both plans has `executed_labels == ["A","B","B","A"]`, positions
`("A1","B1","B2","A2")`, and `plan_sequence_index` `(1,2,3,4)`. Contrast stages
carry a 10/10 `qwen25-1p5b-mlx` / `qwen25-7b-mlx` split, making the interleave
explicit in the manifest as D-014 requires.

**G-9 Full suite** (`python3 -m unittest discover -s tests`, run by the
implementation session): `Ran 2272 tests … OK (skipped=24)`. These are additive,
untracked config files; no existing test references them.

## 8. Evidence base carried forward from the checkpoint (re-verified)

1. **Structural template:** `configs/campaigns/p2_015_floors/05_phase_decode_abba/`
   — 40 members, 10 contiguous A/B/B/A blocks, fixed label order, no RNG; generated
   by `configs/campaigns/p2_015_floors/generate_configs.py`, which freezes
   `calibration_plan.json` + `.sha256` and per-stage `order_manifest.json`
   (`joulewise.order_manifest.v1`) and stamps `calibration-plan-sha256=<hex>` into
   every member's tags. Window C executed exactly this shape and passed — the first
   comparative window in project history to pass its whole-window verdict.
2. **Workload shape:** `df_ph_decode` = 128 prompt / 512 output tokens,
   `repetitions: 1`, `warmup_runs: 1`; sampling `power_hz 10.0`,
   `idle_seconds 30.0`, `warmup_seconds 5.0`. The 7B profile is identical except the
   `model` block, so the contrast isolates the model.
3. **Calibration scope literal:** `production_window` is a member of
   `_CALIBRATION_SCOPES` (`joulewise/detection_floor.py:93-98` — the checkpoint said
   93-96).
4. **Condition-family convention:** `joulewise.condition_family_definition.v1`, an
   exact key set validated by
   `joulewise/floor_extraction.py:280-393`; `comparison_policy` and
   `abba_alias_relation` are frozen literals.
5. **Window structure:** `docs/phase_2/window_runbook.md` — pre-calibration + §5B
   screen, in-window NEG-8 bound corpus (12) + bound mint, start triplet (3),
   science, midpoint (1), science, end triplet (3), post-calibration.
6. **Measured member timings** — see §4.

## 9. What changed from the checkpoint

- 7B model: was absent, now downloaded, verified, revision-pinned (§3).
- 7B member duration: was an unmeasured ~120-130 s size-based inference, now a
  ~97 s probe-anchored figure (§4); the budget fell from ~2.9 h to ~2.6 h.
- Disk: the "~13 GB free" concern was stale; 113 GB free (§3).
- Condition family: the checkpoint's single working-name family
  `sw-decode-1p5b-vs-7b` is **wrong-shaped** and is replaced by two per-arm families
  (§10 Q2), because the manifest validator requires
  `floor_selector.condition_family_ids == [condition_a_id, condition_b_id]` and the
  engine partitions evidence per family id before deriving each arm's stack identity.
- Claim consumption: newly discovered to be blocked (§2). This is the material
  change and the reason §5 is conditional.

## 10. Open questions for magistrate ratification

**Q1 — Which option runs tonight: O1, O2, O3, or O4 (§2)?** This is the decision
that gates everything else. Lieutenant's advisory: O1.

**Q2 — Ratify the two condition-family ids** `sw-decode-a-qwen25-1p5b` and
`sw-decode-b-qwen25-7b` (contrast), and `df-ph-decode-qwen25-7b` (floor). Family ids
and their definition hashes become part of the pre-registration record and later of
artifact cell keys, so renaming them after collection is expensive.

**Q3 — Ratify the new plan-cell vocabulary** `kind: "comparative_contrast"` with
`null_alias: false` and `condition_family_ids: [a, b]`, deliberately distinct from
p2_015's `comparative_abba`. The calibration-plan document has no validator, so this
carries no code risk, but it is a pre-registration vocabulary that later tooling will
have to honour. Alternative considered and rejected: reuse `comparative_abba`, which
would silently label a genuine contrast with the null-alias kind.

**Q4 — Ratify the two-arm `stack_scope.arms` shape** replacing p2_015's scalar
`model_name` / `model_revision` / `model_source`. Again unvalidated; again
pre-registration vocabulary.

**Q5 — Fixed A/B/B/A for all ten blocks, or alternate A/B/B/A and B/A/A/B?** The
checkpoint specified fixed, per existing convention, and
`joulewise/detection_floor.py:2127-2130` hard-requires `["A","B","B","A"]` for
calibration plans. Within-block ABBA already cancels first-order linear drift. A
genuine cross-model contrast could counterbalance harder by alternating the block
form, at the cost of departing from the validated vocabulary. Lieutenant's advisory:
keep fixed.

**Q6 — `calibration_scope` for both plans is `production_window`.** Note that the
existing mint deliberately splits the two scopes — artifact
`CALIBRATION_SCOPE = "production_window"` but `PLAN_DECLARED_SCOPE = "window_a"`
(`scripts/mint_floor_artifact.py:92-93`). A future 7B mint will need its declared
plan scope decided; ratifying `production_window` here pre-commits it.

**Q7 — Arm-A identity, do NOT adopt without a ruling.** Arm A *could* be gated by
the existing floor's exact-cell path if its member configs reproduced window C's
scientific config identity verbatim — i.e. carried the tags `phase2`, `p2-015`,
`window-a`, `floor-calibration`, `df-condition=df-ph-decode` and the p2_015
`hardware_target.notes` string. Lieutenant's advisory: **reject.** Labelling new
production-window members as "p2-015 window-a floor-calibration" to satisfy a hash
is provenance mislabelling, and it does not rescue the contrast anyway because arm B
still has no floor. Recorded so the option is on the record as considered and
refused, not overlooked.

**Q8 — Confirm the `abba_alias_relation: "A_equals_B"` reading.** The
condition-family schema permits no other value
(`joulewise/floor_extraction.py:372-382`), so each arm's family declares a
null-ABBA alias relation even though this campaign's ABBA is a real contrast. The
reading adopted here is that the field describes how that family behaves in its own
*floor calibration*, not how the campaign uses two families against each other.
Confirm or correct.

**Q9 — Bookkeeping owed.** `WINDOW_STATUS.md`'s stale 13 GB disk line; a decision-log
entry for whichever option Q1 selects; registration of the mint-generalization and
analysis-manifest-extension work items surfaced by §2.

exec
/bin/zsh -lc "jq '{schema_version, policy_id, required_environment, cpu_admission, whole_window, calibration, retries, reference_protocol}' configs/campaign_policies/quiet_mac_p2_production.json 2>/dev/null || sed -n '1,240p' configs/campaign_policies/quiet_mac_p2_production.json && rg -n \"network time|systemsetup|displaysleepnow|sudo -n|20 GB|window\" scripts/prewindow_check.sh scripts/quiet_mac_prep.sh | head -n 160" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
{
  "schema_version": "joulewise.campaign_policy.v1",
  "policy_id": "quiet-mac-p2-production",
  "required_environment": null,
  "cpu_admission": null,
  "whole_window": null,
  "calibration": null,
  "retries": null,
  "reference_protocol": null
}
scripts/quiet_mac_prep.sh:2:# quiet_mac_prep.sh — prepare the Mac for a [QUIET-MAC] measurement window.
scripts/quiet_mac_prep.sh:8:KEEP_REGEX='^(Terminal|iTerm2|Finder|SystemUIServer|Dock|loginwindow|WindowServer|coreautha|universalaccessd)$'
scripts/quiet_mac_prep.sh:14:pmset -g batt | grep -q "AC Power" || echo "WARN: not on AC power — plug in before the window."
scripts/quiet_mac_prep.sh:36:# 4. Agent/tooling load check — these MUST be zero during a window.
scripts/quiet_mac_prep.sh:47:if sudo -n /usr/bin/powermetrics -i 200 -n 1 >/dev/null 2>&1; then
scripts/quiet_mac_prep.sh:50:  echo "FAIL: sudo -n powermetrics refused — fix sudoers before the window."
scripts/quiet_mac_prep.sh:83:if pmset displaysleepnow; then
scripts/quiet_mac_prep.sh:114:  echo "FAIL: pmset displaysleepnow failed."
scripts/prewindow_check.sh:2:# Pre-window readiness gate (operator tool; no admin required).
scripts/prewindow_check.sh:5:#   On 2026-07-27 a measurement window failed on its FIRST member, roughly five
scripts/prewindow_check.sh:8:#   member -- but by then the window had been launched, the display slept, and the
scripts/prewindow_check.sh:13:#   window. That is exactly when a window launches. This script checks for them
scripts/prewindow_check.sh:22:#   scripts/prewindow_check.sh                 # check once, report, exit 0/1
scripts/prewindow_check.sh:23:#   scripts/prewindow_check.sh --wait          # wait until ready (default 45 min cap)
scripts/prewindow_check.sh:24:#   scripts/prewindow_check.sh --wait --timeout-min 90
scripts/prewindow_check.sh:25:#   scripts/prewindow_check.sh --window c      # also verify that window's runs roots are clear
scripts/prewindow_check.sh:41:    --window) WINDOW="$2"; shift 2 ;;
scripts/prewindow_check.sh:42:    *) echo "usage: $0 [--wait] [--timeout-min N] [--window LETTER]" >&2; exit 2 ;;
scripts/prewindow_check.sh:51:# Daemons observed or documented to contaminate a quiet window. XProtect is the
scripts/prewindow_check.sh:88:  # 4. Clock pinned. Measurement windows run with automatic network time
scripts/prewindow_check.sh:89:  #    disabled (see scripts/quiet_window_clock.sh); a live adjuster caused two
scripts/prewindow_check.sh:90:  #    window failures on 2026-07-26.
scripts/prewindow_check.sh:92:  nt="$(sudo -n systemsetup -getusingnetworktime 2>/dev/null | sed -n 's/.*Network Time: *//p')"
scripts/prewindow_check.sh:96:    ok "automatic network time disabled (clock pinned)"
scripts/prewindow_check.sh:98:    bad "automatic network time is On -- run scripts/quiet_window_clock.sh disable"
scripts/prewindow_check.sh:102:  # 5. Target window's runs roots must be absent. An occupied slot makes the
scripts/prewindow_check.sh:106:    hits="$(ls -d /Users/edr/code/JouleWise/runs_window_${WINDOW}_* 2>/dev/null | tr '\n' ' ')"
scripts/prewindow_check.sh:108:      bad "runs roots already exist for window ${WINDOW}: $hits"
scripts/prewindow_check.sh:111:      ok "runs roots clear for window ${WINDOW}"
scripts/prewindow_check.sh:115:  # 6. Disk headroom. A window writes a few GB; running out mid-campaign loses it.
scripts/prewindow_check.sh:119:    bad "only ${avail_gb} GB free; a window needs several GB with headroom"
scripts/prewindow_check.sh:127:  procs="$(ps aux | grep -E "codex exec|codex-run|run_campaign|window-chain" | grep -vc grep)"
scripts/prewindow_check.sh:138:bold "Pre-window readiness check — $(date '+%Y-%m-%d %H:%M:%S %Z')"

exec
/bin/zsh -lc "jq 'keys' configs/campaign_policies/quiet_mac_p2_production.json && sed -n '1,220p' configs/campaign_policies/quiet_mac_p2_production.json && sed -n '1,180p' scripts/quiet_mac_prep.sh && sed -n '1,175p' scripts/prewindow_check.sh" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
[
  "calibration_bracketing",
  "cooldown",
  "environment_guard",
  "idle_admission",
  "idle_admission_extension",
  "policy_id",
  "policy_version",
  "post_window_sampling_dwell_s",
  "profile",
  "schema_version"
]
{
  "calibration_bracketing": {
    "calibration_bracket_max_drift_s": 0.01,
    "require_bracket": true
  },
  "cooldown": {
    "absolute_ceiling_w": null,
    "cap_s": 300.0,
    "policy_version": "cooldown-v2",
    "require_thermal_nominal": true,
    "subwindow_s": 5.0,
    "sustained_window_s": 30.0,
    "tolerance_fraction": 0.1
  },
  "environment_guard": {
    "critical_unknown_fail_closed": true,
    "require_ac_power": true,
    "require_displays_asleep": true,
    "require_external_connected": true,
    "require_low_power_mode_off": true,
    "require_screensaver_disengaged": true,
    "require_thermal_nominal": true
  },
  "idle_admission": {
    "enabled": true,
    "on_fail": "abort",
    "retry_attempts": 1
  },
  "idle_admission_extension": {
    "adapter_wattage": {
      "require_known_wattage": true
    },
    "claim_bearing": true,
    "cpu_criteria": {
      "cpu_busy_ratio_p95_max": 0.5,
      "min_samples": 30,
      "on_missing_telemetry": "fail",
      "processor_combined_power_w_p95_max": 1.0
    },
    "neg8_bracket": {
      "max_abs_delta_j": 0.05,
      "max_rel_delta": 0.25,
      "require_bracket": true
    },
    "policy_version": "idle-admission-core-v1",
    "schema_version": "joulewise.idle_admission_extension.v1"
  },
  "policy_id": "quiet-mac-p2-production",
  "policy_version": "environment-guard-cooldown-v2",
  "post_window_sampling_dwell_s": 1.0,
  "profile": "production",
  "schema_version": "joulewise.campaign_policy.v1"
}
#!/bin/bash
# quiet_mac_prep.sh — prepare the Mac for a [QUIET-MAC] measurement window.
# Conservative by design: gracefully quits nonessential USER APPS only,
# reports (never kills) daemons/background load, and prints a quietness
# verdict. Nothing here deletes or force-kills anything.
set -u

KEEP_REGEX='^(Terminal|iTerm2|Finder|SystemUIServer|Dock|loginwindow|WindowServer|coreautha|universalaccessd)$'

echo "== JouleWise quiet-Mac prep $(date -u +%FT%TZ)"

# 1. Power state (no wall meter needed for P2-038/floors; AC is required).
pmset -g batt | head -2
pmset -g batt | grep -q "AC Power" || echo "WARN: not on AC power — plug in before the window."

# 2. Gracefully quit visible nonessential apps.
osascript -e '
tell application "System Events"
  set appList to name of every application process whose background only is false
end tell
return appList' 2>/dev/null | tr ',' '\n' | sed 's/^ *//' | while read -r app; do
  [ -z "$app" ] && continue
  if echo "$app" | grep -Eq "$KEEP_REGEX"; then
    echo "keep : $app"
  else
    echo "quit : $app"
    osascript -e "tell application \"$app\" to quit" >/dev/null 2>&1 &
  fi
done
sleep 5

# 3. Report residual CPU load (top consumers >1% — review, don't kill).
echo "== residual top CPU consumers:"
ps -Aro pcpu,comm | awk '$1>1.0' | head -12

# 4. Agent/tooling load check — these MUST be zero during a window.
echo "== agent-load check (must be empty):"
pgrep -fl "codex exec|codex mcp|claude" | grep -v "$$" || echo "  none"

# 5. Background churn worth knowing about (informational).
echo "== informational:"
pgrep -x mds_stores >/dev/null && echo "  Spotlight (mds_stores) present — fine if idle; check CPU above."
pgrep -x bird >/dev/null && echo "  iCloud sync (bird) present — fine if idle; avoid big file churn."
pgrep -x backupd >/dev/null && echo "  Time Machine backup RUNNING — consider waiting or: sudo tmutil disable"

# 6. powermetrics readiness (D-004 sudoers should make this passwordless).
if sudo -n /usr/bin/powermetrics -i 200 -n 1 >/dev/null 2>&1; then
  echo "OK: passwordless powermetrics works."
else
  echo "FAIL: sudo -n powermetrics refused — fix sudoers before the window."
fi

# 7. Snapshot the configured screensaver and current HID-idle evidence.
# Missing idleTime means the macOS default (20 minutes / 1200 s); no setting
# is written here.
echo "== display/screensaver pre-arm evidence:"
defaults -currentHost read com.apple.screensaver 2>/dev/null || echo "WARN: screensaver defaults probe unavailable."
SCREENSAVER_DELAY_S=$(defaults -currentHost read com.apple.screensaver idleTime 2>/dev/null || echo 1200)
case "$SCREENSAVER_DELAY_S" in
  ''|*[!0-9]*)
    echo "FAIL: unrecognized screensaver idleTime value; state is unknown."
    SCREENSAVER_DELAY_S=""
    ;;
esac
HID_IDLE_NS=$(ioreg -c IOHIDSystem 2>/dev/null | awk -F'= ' '/"HIDIdleTime"/{gsub(/[^0-9]/, "", $2); print $2; exit}')
if [ -n "$HID_IDLE_NS" ] && [ -n "$SCREENSAVER_DELAY_S" ]; then
  HID_IDLE_S=$((HID_IDLE_NS / 1000000000))
  echo "screensaver_delay_s=$SCREENSAVER_DELAY_S hid_idle_s=$HID_IDLE_S"
  if [ "$SCREENSAVER_DELAY_S" -gt 0 ] && [ "$HID_IDLE_S" -ge "$SCREENSAVER_DELAY_S" ]; then
    echo "FAIL: HID idle has reached the configured screensaver delay — dismiss it before arming."
  fi
else
  echo "FAIL: HIDIdleTime probe unavailable."
fi

# 8. Explicit transient arming. This requests display sleep only; it does not
# mutate displaysleep, screensaver, or any other persistent power setting.
echo "== arming display sleep in 5 seconds (move/input now to cancel manually):"
for remaining in 5 4 3 2 1; do
  echo "  $remaining"
  sleep 1
done
if pmset displaysleepnow; then
  sleep 2
  SYSTEMSTATE=$(pmset -g systemstate 2>/dev/null || true)
  echo "$SYSTEMSTATE"
  if echo "$SYSTEMSTATE" | grep -E "Current System Capabilities( are)?:.*Graphics" >/dev/null; then
    echo "FAIL: display verification still reports Graphics capability (any display awake)."
  elif echo "$SYSTEMSTATE" | grep -E "Current System Capabilities( are)?:" >/dev/null; then
    echo "OK: display verification reports all online displays asleep."
  else
    echo "FAIL: unrecognized pmset systemstate output; display state is unknown."
  fi

  # Re-probe screensaver/HID evidence after the display-sleep request. The
  # campaign performs its own equivalent verification before member 1.
  POST_SCREENSAVER_DELAY_S=$(defaults -currentHost read com.apple.screensaver idleTime 2>/dev/null || echo 1200)
  POST_HID_IDLE_NS=$(ioreg -c IOHIDSystem 2>/dev/null | awk -F'= ' '/"HIDIdleTime"/{gsub(/[^0-9]/, "", $2); print $2; exit}')
  case "$POST_SCREENSAVER_DELAY_S" in
    ''|*[!0-9]*) POST_SCREENSAVER_DELAY_S="" ;;
  esac
  if [ -n "$POST_HID_IDLE_NS" ] && [ -n "$POST_SCREENSAVER_DELAY_S" ]; then
    POST_HID_IDLE_S=$((POST_HID_IDLE_NS / 1000000000))
    echo "post_arm_screensaver_delay_s=$POST_SCREENSAVER_DELAY_S post_arm_hid_idle_s=$POST_HID_IDLE_S"
    if [ "$POST_SCREENSAVER_DELAY_S" -eq 0 ] || [ "$POST_HID_IDLE_S" -lt "$POST_SCREENSAVER_DELAY_S" ]; then
      echo "OK: post-arm evidence reports screensaver disengaged."
    else
      echo "FAIL: post-arm HID idle has reached the screensaver delay."
    fi
  else
    echo "FAIL: post-arm screensaver/HID probe unavailable; state is unknown."
  fi
else
  echo "FAIL: pmset displaysleepnow failed."
fi

echo "== verdict: campaign preflight must independently re-probe AC/external power, low-power mode, display sleep, screensaver state, and Nominal thermal pressure before member 1."
#!/bin/bash
# Pre-window readiness gate (operator tool; no admin required).
#
# WHY THIS EXISTS
#   On 2026-07-27 a measurement window failed on its FIRST member, roughly five
#   minutes after launch, because Apple's XProtectRemediator malware scanner was
#   running at 94% CPU. The instrument's CPU-admission gate correctly refused the
#   member -- but by then the window had been launched, the display slept, and the
#   operator had walked away. The failure cost the launch and required a manual
#   diagnose-wait-relaunch cycle.
#
#   Idle-triggered macOS daemons fire in roughly the first ten minutes of a quiet
#   window. That is exactly when a window launches. This script checks for them
#   BEFORE launch, and can wait for them to finish.
#
#   This is a READINESS check, not a measurement gate. It never waives, relaxes,
#   or substitutes for the campaign's own environment and CPU admission gates --
#   those remain authoritative and unchanged. It only avoids launching into a
#   condition those gates will refuse anyway.
#
# USAGE
#   scripts/prewindow_check.sh                 # check once, report, exit 0/1
#   scripts/prewindow_check.sh --wait          # wait until ready (default 45 min cap)
#   scripts/prewindow_check.sh --wait --timeout-min 90
#   scripts/prewindow_check.sh --window c      # also verify that window's runs roots are clear

set -uo pipefail

WAIT=0
TIMEOUT_MIN=45
WINDOW=""
CPU_LIMIT="${CPU_LIMIT:-5.0}"        # percent, per contaminating process
LOAD_LIMIT="${LOAD_LIMIT:-2.0}"      # 1-minute load average
SETTLE_CHECKS=3                      # consecutive clean checks required
INTERVAL_S=30

while [ $# -gt 0 ]; do
  case "$1" in
    --wait) WAIT=1; shift ;;
    --timeout-min) TIMEOUT_MIN="$2"; shift 2 ;;
    --window) WINDOW="$2"; shift 2 ;;
    *) echo "usage: $0 [--wait] [--timeout-min N] [--window LETTER]" >&2; exit 2 ;;
  esac
done

bold() { printf '\033[1m%s\033[0m\n' "$*"; }
ok()   { printf '  \033[32mOK\033[0m    %s\n' "$*"; }
bad()  { printf '  \033[31mBLOCK\033[0m %s\n' "$*"; }
warn() { printf '  \033[33mWARN\033[0m  %s\n' "$*"; }

# Daemons observed or documented to contaminate a quiet window. XProtect is the
# one with a confirmed incident; the rest are the same class and cheap to include.
CONTAMINANTS='XProtect|mds_stores|mdworker|mdbulkimport|backupd|photoanalysisd|softwareupdated|Spotlight|mediaanalysisd'

check_once() {
  local blocked=0

  # 1. Contaminating daemons, by actual CPU use rather than mere presence.
  local busy
  busy="$(ps aux | grep -iE "$CONTAMINANTS" | grep -v grep \
          | awk -v lim="$CPU_LIMIT" '$3+0 > lim {printf "%s(%.1f%%) ", $11, $3}')"
  if [ -n "$busy" ]; then
    bad "background daemon active: $busy"
    blocked=1
  else
    ok "no contaminating daemon above ${CPU_LIMIT}% CPU"
  fi

  # 2. Overall load. A high load average with no named culprit is still a reason
  #    not to launch; the campaign's CPU admission would likely refuse.
  local load1
  load1="$(uptime | sed -n 's/.*load averages*: *\([0-9.]*\).*/\1/p')"
  if awk -v l="$load1" -v m="$LOAD_LIMIT" 'BEGIN{exit !(l+0 > m)}'; then
    bad "1-minute load average ${load1} exceeds ${LOAD_LIMIT}"
    blocked=1
  else
    ok "load average ${load1}"
  fi

  # 3. Power. The production policy requires AC with an external supply.
  if pmset -g batt 2>/dev/null | head -1 | grep -q "AC Power"; then
    ok "on AC power"
  else
    bad "not on AC power"
    blocked=1
  fi

  # 4. Clock pinned. Measurement windows run with automatic network time
  #    disabled (see scripts/quiet_window_clock.sh); a live adjuster caused two
  #    window failures on 2026-07-26.
  local nt
  nt="$(sudo -n systemsetup -getusingnetworktime 2>/dev/null | sed -n 's/.*Network Time: *//p')"
  if [ -z "$nt" ]; then
    warn "cannot read network-time state without admin; confirm the clock is pinned"
  elif [ "$nt" = "Off" ]; then
    ok "automatic network time disabled (clock pinned)"
  else
    bad "automatic network time is On -- run scripts/quiet_window_clock.sh disable"
    blocked=1
  fi

  # 5. Target window's runs roots must be absent. An occupied slot makes the
  #    chain fail late rather than early.
  if [ -n "$WINDOW" ]; then
    local hits
    hits="$(ls -d /Users/edr/code/JouleWise/runs_window_${WINDOW}_* 2>/dev/null | tr '\n' ' ')"
    if [ -n "$hits" ]; then
      bad "runs roots already exist for window ${WINDOW}: $hits"
      blocked=1
    else
      ok "runs roots clear for window ${WINDOW}"
    fi
  fi

  # 6. Disk headroom. A window writes a few GB; running out mid-campaign loses it.
  local avail_gb
  avail_gb="$(df -g /Users/edr/code/JouleWise | awk 'NR==2 {print $4}')"
  if [ "${avail_gb:-0}" -lt 20 ]; then
    bad "only ${avail_gb} GB free; a window needs several GB with headroom"
    blocked=1
  else
    ok "${avail_gb} GB free"
  fi

  # 7. No agent or measurement process already running.
  local procs
  procs="$(ps aux | grep -E "codex exec|codex-run|run_campaign|window-chain" | grep -vc grep)"
  if [ "$procs" -gt 0 ]; then
    bad "$procs agent/measurement process(es) already running"
    blocked=1
  else
    ok "no agent or measurement process running"
  fi

  return $blocked
}

bold "Pre-window readiness check — $(date '+%Y-%m-%d %H:%M:%S %Z')"
if [ "$WAIT" -eq 0 ]; then
  if check_once; then
    bold ""; bold "READY."
    exit 0
  else
    bold ""; bold "NOT READY. Fix the BLOCK lines above, or re-run with --wait."
    exit 1
  fi
fi

# --wait: require SETTLE_CHECKS consecutive clean passes, so a daemon that is
# briefly between bursts does not read as finished.
deadline=$(( $(date +%s) + TIMEOUT_MIN * 60 ))
clean=0
while [ "$(date +%s)" -lt "$deadline" ]; do
  if check_once; then
    clean=$((clean + 1))
    bold "  clean check ${clean}/${SETTLE_CHECKS}"
    if [ "$clean" -ge "$SETTLE_CHECKS" ]; then
      bold ""; bold "READY after $(( ($(date +%s) - (deadline - TIMEOUT_MIN * 60)) / 60 )) min."
      exit 0
    fi
  else
    clean=0
    bold "  not ready; re-checking in ${INTERVAL_S}s"
  fi
  sleep "$INTERVAL_S"
done

bold ""; bold "TIMED OUT after ${TIMEOUT_MIN} min without ${SETTLE_CHECKS} consecutive clean checks."
bold "Do not launch. Investigate what is keeping the machine busy."
exit 1

codex
# Three-Night Quiet-Mac Operator Packet — Draft

**Operator:** Ed  
**Status:** **HOLD until every `[PLACEHOLDER]` and `[BUDGET]` is frozen and the readiness record passes.**

Each night is an independent claim window with fresh roots, calibration bracket, in-window bound, references, verdict, and custody backup.

### Presence legend

- **ED PRESENT:** Ed is physically at the Mac.
- **REMOTE OK:** Allowed only before final arming or after `measurement_complete`.
- **UNATTENDED:** No remote access, agents, browsers, monitoring, log tails, or operator input.

---

# Night 1 — Fresh 1.5B Decode + Prefill Floors

**Window ID:** `[PLACEHOLDER: 1.5B FLOOR WINDOW ID]`  
**Plan root:** `[PLACEHOLDER: PLAN ROOT]`  
**Science configs:** `[PLACEHOLDER: FROZEN CONFIG IDS]`  
**Total duration:** `[BUDGET: TOTAL INCLUDING AT LEAST 20% MARGIN]`  
**Do-not-return-before:** `[BUDGET: COMPLETION TIME/SIGNAL]`

Science payload: the proven decode-floor shape—10 absolute repeats plus 10 null-ABBA blocks/40 members. Prefill floor cells are extracted from these same bundles; they are not optional and are not a separate contrast.

## T-minus preparation — REMOTE OK

- [ ] Readiness record passes with no warning or exception.
- [ ] Reviewed `main` is clean and equals the recorded commit.
- [ ] Plan ID, plan-tree hash, chain hash, policy hash, calibration-acceptance hash, and ledger-head pin are recorded.
- [ ] Exact science membership and order are frozen:
  - before midpoint: `[PLACEHOLDER: STAGE IDS]`
  - after midpoint: `[PLACEHOLDER: STAGE IDS]`
- [ ] Decode and prefill extraction cells, analysis rules, and exact evidence-root mappings are frozen.
- [ ] `waivers.json` is exactly `[]`; the launch and verdict commands contain no waiver argument.
- [ ] Retry policy is frozen. There is no manual or outcome-driven retry.
- [ ] Unique claim, bound, custody, quarantine, and backup paths are named and empty.
- [ ] Both claim and bound backup destinations exist and have sufficient capacity.
- [ ] At least 20 GB disk headroom remains.
- [ ] The pinned 1.5B model, tokenizer, configs, scripts, and virtual environment load locally without downloads.
- [ ] Every stage validates and dry-runs in exact manifest order with no unresolved warning.
- [ ] The frozen budget includes both calibrations, 12 bound members, references 3/1/3, all science, every 180-second settle, and at least 20% margin.

## Arm sequence — ED PRESENT

- [ ] Connect the approved 140 W Anker supply and approved cable. Confirm external AC, `ac_high_power`, low-power mode off, and 140 W negotiated. Do not change them afterward.
- [ ] Finish or pause Time Machine, updates, indexing, downloads, and cloud uploads.
- [ ] Confirm thermal pressure is nominal and passwordless `powermetrics` works.
- [ ] Compare the Mac’s clock with an independent trusted source.
- [ ] Record the existing network-time state:

  ```sh
  sudo systemsetup -getusingnetworktime
  ```

- [ ] Disable automatic network-time adjustment:

  ```sh
  sudo systemsetup -setusingnetworktime off
  ```

- [ ] Run and read the preparation probe:

  ```sh
  bash scripts/quiet_mac_prep.sh
  ```

- [ ] Quit Claude, Codex, t3, browsers, browser automation, monitors, watchers, and log tails. Confirm the final process census is clean.
- [ ] Run the frozen pre-window readiness command:

  ```sh
  bash scripts/prewindow_check.sh --wait \
    --timeout-min [BUDGET] \
    --window [PLACEHOLDER: PREWINDOW LABEL]
  ```

- [ ] Leave the Mac untouched for at least 10 minutes. This also exceeds the required 180-second post-sudo settle.
- [ ] Tell everyone nearby: do not touch the Mac, lid, display, charger, or cable.
- [ ] Launch exactly once from the ordinary foreground shell:

  ```sh
  WINDOW_PLAN_ROOT="[PLACEHOLDER: PLAN ROOT]"
  caffeinate -is /bin/zsh \
    "$WINDOW_PLAN_ROOT/window-chain.zsh" \
    "$WINDOW_PLAN_ROOT"
  ```

- [ ] Use the 20-second arm period to step away. After the one-line arm notice, produce no more operator or remote activity.

## Runs unattended — UNATTENDED

| Approximate point | Automatic work |
|---|---|
| T+0 to `[BUDGET]` | 180-second settle, transient display sleep, pre calibration |
| T+`[BUDGET]` | Pre-calibration level screen; failure stops before science |
| T+`[BUDGET]` | Twelve fresh bound members, then same-window dual-family bound mint |
| T+`[BUDGET]` | Three start references |
| T+`[BUDGET]` | 1.5B decode absolute cell, first null blocks, and frozen prefill-floor extraction basis |
| T+`[BUDGET]` | One midpoint reference |
| T+`[BUDGET]` | Remaining null blocks and frozen prefill-floor extraction basis |
| T+`[BUDGET]` | Three end references |
| T+`[BUDGET]` | Post calibration; together with the pre calibration it forms the bracket |
| T+`[BUDGET]` | `measurement_complete` |

Every campaign invocation performs its own 20-second display arm, fresh environment probe, CPU admission, and 180-second settle. Do not inspect the first member or intervene.

## Morning close-out

- [ ] **ED PRESENT:** Use only the frozen completion signal/no-earlier-than time. Wake the display only after `measurement_complete`.
- [ ] **REMOTE OK:** Reconnect the lead/agent. Finalize all calibration-ledger reservations and commit the exact new ledger-head pin before claim evaluation.
- [ ] Confirm the complete calibration bracket, fresh bound, exact membership, seven references, stable adapter identity, and clean admissions.
- [ ] Emit exactly one ordinary whole-window verdict:

  ```sh
  .venv/bin/python scripts/run_campaign.py \
    --whole-window-verdict \
    --runs-dir "$RUNS_ROOT" \
    --log "$RUNS_ROOT/campaign_log.jsonl" \
    --campaign-policy configs/campaign_policies/quiet_mac_p2_production.json \
    --neg8-drift-bound "$BOUND_RUNS_ROOT/neg8-drift-bound.json"
  ```

- [ ] Require `status: passed`; record the evaluation-basis SHA-256.
- [ ] Release any intentionally stopped cloud-sync process using its fail-safe cleanup.
- [ ] Back up both immutable roots; require exit code `0` twice:

  ```sh
  bash scripts/backup_runs.sh "$RUNS_ROOT" "$CLAIM_BACKUP_DEST"
  bash scripts/backup_runs.sh "$BOUND_RUNS_ROOT" "$BOUND_BACKUP_DEST"
  ```

- [ ] **ED PRESENT:** Restore and verify automatic network time:

  ```sh
  sudo systemsetup -setusingnetworktime on
  sudo systemsetup -getusingnetworktime
  ```

- [ ] Keep governed extraction and floor analysis in the same lead-controlled custody session.
- [ ] Call the night claim-bearing only after verdict, both backups, and extraction all pass.

**Send the agent:** window/plan IDs; commit and policy hash; claim, bound, and custody roots; `measurement_complete` timestamp; pre/post calibration directories; verdict status and basis SHA; both backup destinations and exit codes; network-time off/on timestamps; and every failed, quarantined, or superseded occurrence.

---

# Night 2 — Fresh 7B Decode + Prefill Floors

**Window ID:** `[PLACEHOLDER: 7B FLOOR WINDOW ID]`  
**Plan root:** `[PLACEHOLDER: PLAN ROOT]`  
**Science configs:** `[PLACEHOLDER: FROZEN CONFIG IDS]`  
**Total duration:** `[BUDGET: TOTAL INCLUDING AT LEAST 20% MARGIN]`  
**Do-not-return-before:** `[BUDGET: COMPLETION TIME/SIGNAL]`

Science payload: 10 decode absolute repeats plus 10 null-ABBA blocks/40 members on the frozen 7B stack. Prefill floor cells come from the same bundles and must be included in the frozen extraction.

## T-minus preparation — REMOTE OK

- [ ] Readiness record passes with no exception.
- [ ] Clean reviewed commit, policy hash, calibration-acceptance hash, ledger head, plan hash, and launcher hash are recorded.
- [ ] Exact stages are frozen:
  - before midpoint: `[PLACEHOLDER: 7B ABSOLUTE + NULL BLOCKS 1–5 CONFIG IDS]`
  - after midpoint: `[PLACEHOLDER: 7B NULL BLOCKS 6–10 CONFIG IDS]`
- [ ] Decode and prefill cells, analysis rules, extraction spec, evidence roots, and counts are frozen.
- [ ] `waivers.json` is exactly `[]`; retry policy is frozen.
- [ ] Fresh claim, bound, custody, quarantine, and backup paths are named and empty.
- [ ] Both 1.5B reference-model and 7B science-model snapshots are complete, revision-correct, and usable offline.
- [ ] Every stage validates and dry-runs in exact order.
- [ ] Disk and both backup destinations have sufficient headroom.
- [ ] Budget includes the 7B cold first load, all settles, calibrations, bound corpus, references, science, and at least 20% margin.

## Arm sequence — ED PRESENT

- [ ] Connect and verify the approved charger/cable: external AC, 140 W negotiated, `ac_high_power`, low-power mode off.
- [ ] Finish or pause background maintenance and cloud transfers.
- [ ] Confirm nominal thermal state and passwordless `powermetrics`.
- [ ] Verify the clock against an independent source.
- [ ] Record and disable automatic network time:

  ```sh
  sudo systemsetup -getusingnetworktime
  sudo systemsetup -setusingnetworktime off
  ```

- [ ] Run `bash scripts/quiet_mac_prep.sh`; resolve every failure.
- [ ] Quit all agents, t3, browsers, automation, monitors, watchers, and tails; require a clean census.
- [ ] Run the frozen `prewindow_check.sh --wait` command and require `READY`.
- [ ] Leave the Mac untouched for at least 10 minutes.
- [ ] Tell everyone nearby not to touch the machine or power path.
- [ ] Launch exactly once:

  ```sh
  WINDOW_PLAN_ROOT="[PLACEHOLDER: PLAN ROOT]"
  caffeinate -is /bin/zsh \
    "$WINDOW_PLAN_ROOT/window-chain.zsh" \
    "$WINDOW_PLAN_ROOT"
  ```

- [ ] Step away during the 20-second arm. No remote or local monitoring afterward.

## Runs unattended — UNATTENDED

| Approximate point | Automatic work |
|---|---|
| T+0 to `[BUDGET]` | Settle, transient display sleep, pre calibration and level screen |
| T+`[BUDGET]` | Twelve fresh bound members and same-window bound mint |
| T+`[BUDGET]` | Three start references |
| T+`[BUDGET]` | 7B absolute cell and null blocks 1–5; prefill evidence rides the same bundles |
| T+`[BUDGET]` | One midpoint reference |
| T+`[BUDGET]` | 7B null blocks 6–10; remaining prefill evidence |
| T+`[BUDGET]` | Three end references |
| T+`[BUDGET]` | Post calibration and bracket closure |
| T+`[BUDGET]` | `measurement_complete` |

The first 7B member may take longer because it reads the local model snapshot cold. That alone is not a failure and is not a reason to intervene.

## Morning close-out

- [ ] **ED PRESENT:** Confirm `measurement_complete` before waking or touching anything.
- [ ] **REMOTE OK:** Reconnect the lead/agent; finalize calibration receipts and commit the new ledger-head pin.
- [ ] Authenticate the calibration bracket, fresh bound, exact science basis, 3/1/3 references, CPU admission, and adapter continuity.
- [ ] Emit exactly one whole-window verdict and require `status: passed`.
- [ ] Record the evaluation-basis SHA-256.
- [ ] Release any stopped cloud-sync process safely.
- [ ] Back up claim and bound roots separately; require exit `0` for both.
- [ ] **ED PRESENT:** Restore automatic network time and verify it is on.
- [ ] Run governed extraction for both 7B decode and 7B prefill floor cells in the same custody session as the consuming analysis.
- [ ] Do not advance to the contrast night until the required 1.5B and 7B floor artifacts, custody, and head pins are ready.

**Send the agent:** all identifiers and roots; completion timestamp; pre/post calibration directories; exact member/failure inventory; verdict row and basis SHA; both backup receipts; network-time timestamps; and the decode/prefill extraction paths.

---

# Night 3 — Fresh 1.5B-vs-7B Decode Contrast

**Window ID:** `[PLACEHOLDER: DECODE CONTRAST WINDOW ID]`  
**Plan root:** `[PLACEHOLDER: PLAN ROOT]`  
**Science configs:** `[PLACEHOLDER: CONTRAST CONFIG IDS]`  
**1.5B floor artifact:** `[PLACEHOLDER: FROZEN ARTIFACT ID/HASH]`  
**7B floor artifact:** `[PLACEHOLDER: FROZEN ARTIFACT ID/HASH]`  
**Total duration:** `[BUDGET: TOTAL INCLUDING AT LEAST 20% MARGIN]`  
**Do-not-return-before:** `[BUDGET: COMPLETION TIME/SIGNAL]`

Science payload: decode only—10 fixed A/B/B/A blocks, 40 members total. Blocks 1–5 run before the midpoint reference and blocks 6–10 after it. Do not add a prefill contrast to this night.

## T-minus preparation — REMOTE OK

- [ ] Both preceding floor windows have passed their verdict, backup, extraction, and custody gates.
- [ ] Exact 1.5B and 7B floor artifact IDs, hashes, stack identities, and ledger-head pins are frozen into the contrast plan.
- [ ] Readiness record passes with no exception.
- [ ] Reviewed commit, policy, acceptance artifact, ledger head, plan tree, chain, and exact evidence-root mappings are recorded.
- [ ] Contrast membership is frozen: 10 complete A/B/B/A blocks; no optional member, top-up, block deletion, or outcome-driven replacement.
- [ ] Stage split is frozen:
  - before midpoint: `[PLACEHOLDER: BLOCKS 1–5 CONFIG ID]`
  - after midpoint: `[PLACEHOLDER: BLOCKS 6–10 CONFIG ID]`
- [ ] Both model snapshots and tokenizers are complete, revision-correct, and available offline.
- [ ] `waivers.json` is exactly `[]`; retry policy and analysis direction are frozen.
- [ ] Fresh claim, bound, custody, quarantine, and backup paths are named and empty.
- [ ] Every config validates and both stages dry-run in exact manifest order.
- [ ] Budget includes two-model load churn, all settles, calibrations, bound corpus, references, science, and at least 20% margin.

## Arm sequence — ED PRESENT

- [ ] Verify approved power supply/cable, external AC, 140 W negotiation, high-power policy, and low-power mode off.
- [ ] Finish or pause maintenance, updates, indexing, backups, downloads, and cloud uploads.
- [ ] Confirm nominal thermal state and passwordless `powermetrics`.
- [ ] Verify the clock independently; record and disable automatic network time:

  ```sh
  sudo systemsetup -getusingnetworktime
  sudo systemsetup -setusingnetworktime off
  ```

- [ ] Run `bash scripts/quiet_mac_prep.sh`; resolve every failure.
- [ ] Quit every agent, t3, browser, automation session, monitor, watcher, and tail. Require a zero-survivor census.
- [ ] Run the frozen `prewindow_check.sh --wait` command and require `READY`.
- [ ] Leave the Mac untouched for at least 10 minutes.
- [ ] Tell everyone nearby not to touch the Mac or its power path.
- [ ] Launch exactly once:

  ```sh
  WINDOW_PLAN_ROOT="[PLACEHOLDER: PLAN ROOT]"
  caffeinate -is /bin/zsh \
    "$WINDOW_PLAN_ROOT/window-chain.zsh" \
    "$WINDOW_PLAN_ROOT"
  ```

- [ ] Walk away during the 20-second arm. Do not monitor either model’s progress.

## Runs unattended — UNATTENDED

| Approximate point | Automatic work |
|---|---|
| T+0 to `[BUDGET]` | Settle, transient display sleep, pre calibration and level screen |
| T+`[BUDGET]` | Twelve fresh bound members and same-window bound mint |
| T+`[BUDGET]` | Three start references |
| T+`[BUDGET]` | Decode contrast blocks 1–5 |
| T+`[BUDGET]` | One midpoint reference |
| T+`[BUDGET]` | Decode contrast blocks 6–10 |
| T+`[BUDGET]` | Three end references |
| T+`[BUDGET]` | Post calibration and bracket closure |
| T+`[BUDGET]` | `measurement_complete` |

Alternating models causes ordinary load-time variation. Never use observed run time or apparent effect size to add, drop, reorder, or rerun a block.

## Morning close-out

- [ ] **ED PRESENT:** Confirm `measurement_complete` before waking the display.
- [ ] **REMOTE OK:** Reconnect the lead/agent; finalize calibration receipts and commit the exact ledger-head pin.
- [ ] Authenticate the bracket, bound, 3/1/3 references, all 10 complete blocks, both stack identities, CPU admission, and stable power identity.
- [ ] Emit exactly one ordinary whole-window verdict; require `status: passed`.
- [ ] Record its exact evaluation-basis SHA-256.
- [ ] Release any stopped cloud-sync process using the frozen cleanup.
- [ ] Back up claim and bound roots separately; require two exit-`0` receipts.
- [ ] **ED PRESENT:** Restore and verify automatic network time.
- [ ] Run exact-basis contrast extraction and analysis against the frozen 1.5B and 7B floors in the same custody session.
- [ ] Report the frozen directional result even if it does not clear the decision envelope. Never top up the campaign.

**Send the agent:** window/plan and both floor IDs; code, policy, and ledger pins; all roots; completion timestamp; calibration directories; exact ten-block inventory; verdict and basis SHA; backup receipts; network-time timestamps; extraction path; and every refusal or deviation.

---

# ABORT Page — Stop, Preserve, Diagnose

A failed night is still evidence. It is not permission to clean up and try again.

## Treat the night as failed or non-claim-bearing if any of these occurs

- The chain stops before `measurement_complete`.
- The pre-calibration level screen aborts before member 1.
- A display wakes, the screensaver engages, or anyone touches the Mac.
- CPU, thermal, clock, environment, or adapter admission refuses.
- The charger, cable, wattage, lid, or power policy changes.
- A member is incomplete, fallback-anchored, duplicated, missing, or occupies an existing slot.
- A science stage does not complete its exact frozen membership.
- The post calibration is missing or invalid.
- The calibration ledger has a pending, malformed, or conflicting receipt.
- The whole-window verdict is anything other than `passed`.
- Either custody backup fails.
- Extraction refuses membership or reports that not all frozen cells are extractable.

## What to do immediately

- [ ] Stop touching the machine. Let the foreground chain stop on its own unless safety requires intervention.
- [ ] Record the visible failure and time without altering any artifact.
- [ ] Preserve the complete claim root, bound root, calibration directories, campaign logs, operator logs, locks, and partial bundles.
- [ ] Mark the night **ABORTED / NOT CLAIM-BEARING** until the lead establishes a stronger valid status.
- [ ] Restore automatic network time only after the stopped state and available custody have been recorded.
- [ ] Send the lead/agent the exact roots, last completed stage, failure text, timestamp, process or power change observed, and whether `measurement_complete` exists.

## Never do these things

- **Never delete, overwrite, truncate, or “clean up” failed evidence.**
- **Never retry until a specific cause has been identified, removed, verified, and shown to be retryable by the frozen plan.**
- Never rerun merely because a calibration number, energy result, or verdict was unfavorable.
- Never change a threshold, waiver, membership list, model identity, stage order, analysis rule, or retry count during the night.
- Never use an environment override.
- Never borrow a calibration or bound from another night.
- Never hand-patch metadata, hashes, calibration bounds, or drift allowances.
- Never add members, drop blocks, or top up to improve significance.
- Never append a different verdict over the same basis.
- Never delete an unreadable lock blindly; establish whether its PID is live.
- Never reuse a contaminated root as though it were fresh.
- Never treat a failed backup as permission to alter the source.
- Never wake the display or reconnect remotely simply to check progress.

One automatic settled retry is permitted only when the chain itself identifies a calibration failure whose sole reason is the allowed clock-anchor condition. Any other retry requires the frozen cause-removal rule. With no named removable cause, the night ends.
tokens used
86,813
# Three-Night Quiet-Mac Operator Packet — Draft

**Operator:** Ed  
**Status:** **HOLD until every `[PLACEHOLDER]` and `[BUDGET]` is frozen and the readiness record passes.**

Each night is an independent claim window with fresh roots, calibration bracket, in-window bound, references, verdict, and custody backup.

### Presence legend

- **ED PRESENT:** Ed is physically at the Mac.
- **REMOTE OK:** Allowed only before final arming or after `measurement_complete`.
- **UNATTENDED:** No remote access, agents, browsers, monitoring, log tails, or operator input.

---

# Night 1 — Fresh 1.5B Decode + Prefill Floors

**Window ID:** `[PLACEHOLDER: 1.5B FLOOR WINDOW ID]`  
**Plan root:** `[PLACEHOLDER: PLAN ROOT]`  
**Science configs:** `[PLACEHOLDER: FROZEN CONFIG IDS]`  
**Total duration:** `[BUDGET: TOTAL INCLUDING AT LEAST 20% MARGIN]`  
**Do-not-return-before:** `[BUDGET: COMPLETION TIME/SIGNAL]`

Science payload: the proven decode-floor shape—10 absolute repeats plus 10 null-ABBA blocks/40 members. Prefill floor cells are extracted from these same bundles; they are not optional and are not a separate contrast.

## T-minus preparation — REMOTE OK

- [ ] Readiness record passes with no warning or exception.
- [ ] Reviewed `main` is clean and equals the recorded commit.
- [ ] Plan ID, plan-tree hash, chain hash, policy hash, calibration-acceptance hash, and ledger-head pin are recorded.
- [ ] Exact science membership and order are frozen:
  - before midpoint: `[PLACEHOLDER: STAGE IDS]`
  - after midpoint: `[PLACEHOLDER: STAGE IDS]`
- [ ] Decode and prefill extraction cells, analysis rules, and exact evidence-root mappings are frozen.
- [ ] `waivers.json` is exactly `[]`; the launch and verdict commands contain no waiver argument.
- [ ] Retry policy is frozen. There is no manual or outcome-driven retry.
- [ ] Unique claim, bound, custody, quarantine, and backup paths are named and empty.
- [ ] Both claim and bound backup destinations exist and have sufficient capacity.
- [ ] At least 20 GB disk headroom remains.
- [ ] The pinned 1.5B model, tokenizer, configs, scripts, and virtual environment load locally without downloads.
- [ ] Every stage validates and dry-runs in exact manifest order with no unresolved warning.
- [ ] The frozen budget includes both calibrations, 12 bound members, references 3/1/3, all science, every 180-second settle, and at least 20% margin.

## Arm sequence — ED PRESENT

- [ ] Connect the approved 140 W Anker supply and approved cable. Confirm external AC, `ac_high_power`, low-power mode off, and 140 W negotiated. Do not change them afterward.
- [ ] Finish or pause Time Machine, updates, indexing, downloads, and cloud uploads.
- [ ] Confirm thermal pressure is nominal and passwordless `powermetrics` works.
- [ ] Compare the Mac’s clock with an independent trusted source.
- [ ] Record the existing network-time state:

  ```sh
  sudo systemsetup -getusingnetworktime
  ```

- [ ] Disable automatic network-time adjustment:

  ```sh
  sudo systemsetup -setusingnetworktime off
  ```

- [ ] Run and read the preparation probe:

  ```sh
  bash scripts/quiet_mac_prep.sh
  ```

- [ ] Quit Claude, Codex, t3, browsers, browser automation, monitors, watchers, and log tails. Confirm the final process census is clean.
- [ ] Run the frozen pre-window readiness command:

  ```sh
  bash scripts/prewindow_check.sh --wait \
    --timeout-min [BUDGET] \
    --window [PLACEHOLDER: PREWINDOW LABEL]
  ```

- [ ] Leave the Mac untouched for at least 10 minutes. This also exceeds the required 180-second post-sudo settle.
- [ ] Tell everyone nearby: do not touch the Mac, lid, display, charger, or cable.
- [ ] Launch exactly once from the ordinary foreground shell:

  ```sh
  WINDOW_PLAN_ROOT="[PLACEHOLDER: PLAN ROOT]"
  caffeinate -is /bin/zsh \
    "$WINDOW_PLAN_ROOT/window-chain.zsh" \
    "$WINDOW_PLAN_ROOT"
  ```

- [ ] Use the 20-second arm period to step away. After the one-line arm notice, produce no more operator or remote activity.

## Runs unattended — UNATTENDED

| Approximate point | Automatic work |
|---|---|
| T+0 to `[BUDGET]` | 180-second settle, transient display sleep, pre calibration |
| T+`[BUDGET]` | Pre-calibration level screen; failure stops before science |
| T+`[BUDGET]` | Twelve fresh bound members, then same-window dual-family bound mint |
| T+`[BUDGET]` | Three start references |
| T+`[BUDGET]` | 1.5B decode absolute cell, first null blocks, and frozen prefill-floor extraction basis |
| T+`[BUDGET]` | One midpoint reference |
| T+`[BUDGET]` | Remaining null blocks and frozen prefill-floor extraction basis |
| T+`[BUDGET]` | Three end references |
| T+`[BUDGET]` | Post calibration; together with the pre calibration it forms the bracket |
| T+`[BUDGET]` | `measurement_complete` |

Every campaign invocation performs its own 20-second display arm, fresh environment probe, CPU admission, and 180-second settle. Do not inspect the first member or intervene.

## Morning close-out

- [ ] **ED PRESENT:** Use only the frozen completion signal/no-earlier-than time. Wake the display only after `measurement_complete`.
- [ ] **REMOTE OK:** Reconnect the lead/agent. Finalize all calibration-ledger reservations and commit the exact new ledger-head pin before claim evaluation.
- [ ] Confirm the complete calibration bracket, fresh bound, exact membership, seven references, stable adapter identity, and clean admissions.
- [ ] Emit exactly one ordinary whole-window verdict:

  ```sh
  .venv/bin/python scripts/run_campaign.py \
    --whole-window-verdict \
    --runs-dir "$RUNS_ROOT" \
    --log "$RUNS_ROOT/campaign_log.jsonl" \
    --campaign-policy configs/campaign_policies/quiet_mac_p2_production.json \
    --neg8-drift-bound "$BOUND_RUNS_ROOT/neg8-drift-bound.json"
  ```

- [ ] Require `status: passed`; record the evaluation-basis SHA-256.
- [ ] Release any intentionally stopped cloud-sync process using its fail-safe cleanup.
- [ ] Back up both immutable roots; require exit code `0` twice:

  ```sh
  bash scripts/backup_runs.sh "$RUNS_ROOT" "$CLAIM_BACKUP_DEST"
  bash scripts/backup_runs.sh "$BOUND_RUNS_ROOT" "$BOUND_BACKUP_DEST"
  ```

- [ ] **ED PRESENT:** Restore and verify automatic network time:

  ```sh
  sudo systemsetup -setusingnetworktime on
  sudo systemsetup -getusingnetworktime
  ```

- [ ] Keep governed extraction and floor analysis in the same lead-controlled custody session.
- [ ] Call the night claim-bearing only after verdict, both backups, and extraction all pass.

**Send the agent:** window/plan IDs; commit and policy hash; claim, bound, and custody roots; `measurement_complete` timestamp; pre/post calibration directories; verdict status and basis SHA; both backup destinations and exit codes; network-time off/on timestamps; and every failed, quarantined, or superseded occurrence.

---

# Night 2 — Fresh 7B Decode + Prefill Floors

**Window ID:** `[PLACEHOLDER: 7B FLOOR WINDOW ID]`  
**Plan root:** `[PLACEHOLDER: PLAN ROOT]`  
**Science configs:** `[PLACEHOLDER: FROZEN CONFIG IDS]`  
**Total duration:** `[BUDGET: TOTAL INCLUDING AT LEAST 20% MARGIN]`  
**Do-not-return-before:** `[BUDGET: COMPLETION TIME/SIGNAL]`

Science payload: 10 decode absolute repeats plus 10 null-ABBA blocks/40 members on the frozen 7B stack. Prefill floor cells come from the same bundles and must be included in the frozen extraction.

## T-minus preparation — REMOTE OK

- [ ] Readiness record passes with no exception.
- [ ] Clean reviewed commit, policy hash, calibration-acceptance hash, ledger head, plan hash, and launcher hash are recorded.
- [ ] Exact stages are frozen:
  - before midpoint: `[PLACEHOLDER: 7B ABSOLUTE + NULL BLOCKS 1–5 CONFIG IDS]`
  - after midpoint: `[PLACEHOLDER: 7B NULL BLOCKS 6–10 CONFIG IDS]`
- [ ] Decode and prefill cells, analysis rules, extraction spec, evidence roots, and counts are frozen.
- [ ] `waivers.json` is exactly `[]`; retry policy is frozen.
- [ ] Fresh claim, bound, custody, quarantine, and backup paths are named and empty.
- [ ] Both 1.5B reference-model and 7B science-model snapshots are complete, revision-correct, and usable offline.
- [ ] Every stage validates and dry-runs in exact order.
- [ ] Disk and both backup destinations have sufficient headroom.
- [ ] Budget includes the 7B cold first load, all settles, calibrations, bound corpus, references, science, and at least 20% margin.

## Arm sequence — ED PRESENT

- [ ] Connect and verify the approved charger/cable: external AC, 140 W negotiated, `ac_high_power`, low-power mode off.
- [ ] Finish or pause background maintenance and cloud transfers.
- [ ] Confirm nominal thermal state and passwordless `powermetrics`.
- [ ] Verify the clock against an independent source.
- [ ] Record and disable automatic network time:

  ```sh
  sudo systemsetup -getusingnetworktime
  sudo systemsetup -setusingnetworktime off
  ```

- [ ] Run `bash scripts/quiet_mac_prep.sh`; resolve every failure.
- [ ] Quit all agents, t3, browsers, automation, monitors, watchers, and tails; require a clean census.
- [ ] Run the frozen `prewindow_check.sh --wait` command and require `READY`.
- [ ] Leave the Mac untouched for at least 10 minutes.
- [ ] Tell everyone nearby not to touch the machine or power path.
- [ ] Launch exactly once:

  ```sh
  WINDOW_PLAN_ROOT="[PLACEHOLDER: PLAN ROOT]"
  caffeinate -is /bin/zsh \
    "$WINDOW_PLAN_ROOT/window-chain.zsh" \
    "$WINDOW_PLAN_ROOT"
  ```

- [ ] Step away during the 20-second arm. No remote or local monitoring afterward.

## Runs unattended — UNATTENDED

| Approximate point | Automatic work |
|---|---|
| T+0 to `[BUDGET]` | Settle, transient display sleep, pre calibration and level screen |
| T+`[BUDGET]` | Twelve fresh bound members and same-window bound mint |
| T+`[BUDGET]` | Three start references |
| T+`[BUDGET]` | 7B absolute cell and null blocks 1–5; prefill evidence rides the same bundles |
| T+`[BUDGET]` | One midpoint reference |
| T+`[BUDGET]` | 7B null blocks 6–10; remaining prefill evidence |
| T+`[BUDGET]` | Three end references |
| T+`[BUDGET]` | Post calibration and bracket closure |
| T+`[BUDGET]` | `measurement_complete` |

The first 7B member may take longer because it reads the local model snapshot cold. That alone is not a failure and is not a reason to intervene.

## Morning close-out

- [ ] **ED PRESENT:** Confirm `measurement_complete` before waking or touching anything.
- [ ] **REMOTE OK:** Reconnect the lead/agent; finalize calibration receipts and commit the new ledger-head pin.
- [ ] Authenticate the calibration bracket, fresh bound, exact science basis, 3/1/3 references, CPU admission, and adapter continuity.
- [ ] Emit exactly one whole-window verdict and require `status: passed`.
- [ ] Record the evaluation-basis SHA-256.
- [ ] Release any stopped cloud-sync process safely.
- [ ] Back up claim and bound roots separately; require exit `0` for both.
- [ ] **ED PRESENT:** Restore automatic network time and verify it is on.
- [ ] Run governed extraction for both 7B decode and 7B prefill floor cells in the same custody session as the consuming analysis.
- [ ] Do not advance to the contrast night until the required 1.5B and 7B floor artifacts, custody, and head pins are ready.

**Send the agent:** all identifiers and roots; completion timestamp; pre/post calibration directories; exact member/failure inventory; verdict row and basis SHA; both backup receipts; network-time timestamps; and the decode/prefill extraction paths.

---

# Night 3 — Fresh 1.5B-vs-7B Decode Contrast

**Window ID:** `[PLACEHOLDER: DECODE CONTRAST WINDOW ID]`  
**Plan root:** `[PLACEHOLDER: PLAN ROOT]`  
**Science configs:** `[PLACEHOLDER: CONTRAST CONFIG IDS]`  
**1.5B floor artifact:** `[PLACEHOLDER: FROZEN ARTIFACT ID/HASH]`  
**7B floor artifact:** `[PLACEHOLDER: FROZEN ARTIFACT ID/HASH]`  
**Total duration:** `[BUDGET: TOTAL INCLUDING AT LEAST 20% MARGIN]`  
**Do-not-return-before:** `[BUDGET: COMPLETION TIME/SIGNAL]`

Science payload: decode only—10 fixed A/B/B/A blocks, 40 members total. Blocks 1–5 run before the midpoint reference and blocks 6–10 after it. Do not add a prefill contrast to this night.

## T-minus preparation — REMOTE OK

- [ ] Both preceding floor windows have passed their verdict, backup, extraction, and custody gates.
- [ ] Exact 1.5B and 7B floor artifact IDs, hashes, stack identities, and ledger-head pins are frozen into the contrast plan.
- [ ] Readiness record passes with no exception.
- [ ] Reviewed commit, policy, acceptance artifact, ledger head, plan tree, chain, and exact evidence-root mappings are recorded.
- [ ] Contrast membership is frozen: 10 complete A/B/B/A blocks; no optional member, top-up, block deletion, or outcome-driven replacement.
- [ ] Stage split is frozen:
  - before midpoint: `[PLACEHOLDER: BLOCKS 1–5 CONFIG ID]`
  - after midpoint: `[PLACEHOLDER: BLOCKS 6–10 CONFIG ID]`
- [ ] Both model snapshots and tokenizers are complete, revision-correct, and available offline.
- [ ] `waivers.json` is exactly `[]`; retry policy and analysis direction are frozen.
- [ ] Fresh claim, bound, custody, quarantine, and backup paths are named and empty.
- [ ] Every config validates and both stages dry-run in exact manifest order.
- [ ] Budget includes two-model load churn, all settles, calibrations, bound corpus, references, science, and at least 20% margin.

## Arm sequence — ED PRESENT

- [ ] Verify approved power supply/cable, external AC, 140 W negotiation, high-power policy, and low-power mode off.
- [ ] Finish or pause maintenance, updates, indexing, backups, downloads, and cloud uploads.
- [ ] Confirm nominal thermal state and passwordless `powermetrics`.
- [ ] Verify the clock independently; record and disable automatic network time:

  ```sh
  sudo systemsetup -getusingnetworktime
  sudo systemsetup -setusingnetworktime off
  ```

- [ ] Run `bash scripts/quiet_mac_prep.sh`; resolve every failure.
- [ ] Quit every agent, t3, browser, automation session, monitor, watcher, and tail. Require a zero-survivor census.
- [ ] Run the frozen `prewindow_check.sh --wait` command and require `READY`.
- [ ] Leave the Mac untouched for at least 10 minutes.
- [ ] Tell everyone nearby not to touch the Mac or its power path.
- [ ] Launch exactly once:

  ```sh
  WINDOW_PLAN_ROOT="[PLACEHOLDER: PLAN ROOT]"
  caffeinate -is /bin/zsh \
    "$WINDOW_PLAN_ROOT/window-chain.zsh" \
    "$WINDOW_PLAN_ROOT"
  ```

- [ ] Walk away during the 20-second arm. Do not monitor either model’s progress.

## Runs unattended — UNATTENDED

| Approximate point | Automatic work |
|---|---|
| T+0 to `[BUDGET]` | Settle, transient display sleep, pre calibration and level screen |
| T+`[BUDGET]` | Twelve fresh bound members and same-window bound mint |
| T+`[BUDGET]` | Three start references |
| T+`[BUDGET]` | Decode contrast blocks 1–5 |
| T+`[BUDGET]` | One midpoint reference |
| T+`[BUDGET]` | Decode contrast blocks 6–10 |
| T+`[BUDGET]` | Three end references |
| T+`[BUDGET]` | Post calibration and bracket closure |
| T+`[BUDGET]` | `measurement_complete` |

Alternating models causes ordinary load-time variation. Never use observed run time or apparent effect size to add, drop, reorder, or rerun a block.

## Morning close-out

- [ ] **ED PRESENT:** Confirm `measurement_complete` before waking the display.
- [ ] **REMOTE OK:** Reconnect the lead/agent; finalize calibration receipts and commit the exact ledger-head pin.
- [ ] Authenticate the bracket, bound, 3/1/3 references, all 10 complete blocks, both stack identities, CPU admission, and stable power identity.
- [ ] Emit exactly one ordinary whole-window verdict; require `status: passed`.
- [ ] Record its exact evaluation-basis SHA-256.
- [ ] Release any stopped cloud-sync process using the frozen cleanup.
- [ ] Back up claim and bound roots separately; require two exit-`0` receipts.
- [ ] **ED PRESENT:** Restore and verify automatic network time.
- [ ] Run exact-basis contrast extraction and analysis against the frozen 1.5B and 7B floors in the same custody session.
- [ ] Report the frozen directional result even if it does not clear the decision envelope. Never top up the campaign.

**Send the agent:** window/plan and both floor IDs; code, policy, and ledger pins; all roots; completion timestamp; calibration directories; exact ten-block inventory; verdict and basis SHA; backup receipts; network-time timestamps; extraction path; and every refusal or deviation.

---

# ABORT Page — Stop, Preserve, Diagnose

A failed night is still evidence. It is not permission to clean up and try again.

## Treat the night as failed or non-claim-bearing if any of these occurs

- The chain stops before `measurement_complete`.
- The pre-calibration level screen aborts before member 1.
- A display wakes, the screensaver engages, or anyone touches the Mac.
- CPU, thermal, clock, environment, or adapter admission refuses.
- The charger, cable, wattage, lid, or power policy changes.
- A member is incomplete, fallback-anchored, duplicated, missing, or occupies an existing slot.
- A science stage does not complete its exact frozen membership.
- The post calibration is missing or invalid.
- The calibration ledger has a pending, malformed, or conflicting receipt.
- The whole-window verdict is anything other than `passed`.
- Either custody backup fails.
- Extraction refuses membership or reports that not all frozen cells are extractable.

## What to do immediately

- [ ] Stop touching the machine. Let the foreground chain stop on its own unless safety requires intervention.
- [ ] Record the visible failure and time without altering any artifact.
- [ ] Preserve the complete claim root, bound root, calibration directories, campaign logs, operator logs, locks, and partial bundles.
- [ ] Mark the night **ABORTED / NOT CLAIM-BEARING** until the lead establishes a stronger valid status.
- [ ] Restore automatic network time only after the stopped state and available custody have been recorded.
- [ ] Send the lead/agent the exact roots, last completed stage, failure text, timestamp, process or power change observed, and whether `measurement_complete` exists.

## Never do these things

- **Never delete, overwrite, truncate, or “clean up” failed evidence.**
- **Never retry until a specific cause has been identified, removed, verified, and shown to be retryable by the frozen plan.**
- Never rerun merely because a calibration number, energy result, or verdict was unfavorable.
- Never change a threshold, waiver, membership list, model identity, stage order, analysis rule, or retry count during the night.
- Never use an environment override.
- Never borrow a calibration or bound from another night.
- Never hand-patch metadata, hashes, calibration bounds, or drift allowances.
- Never add members, drop blocks, or top up to improve significance.
- Never append a different verdict over the same basis.
- Never delete an unreadable lock blindly; establish whether its PID is live.
- Never reuse a contaminated root as though it were fresh.
- Never treat a failed backup as permission to alter the source.
- Never wake the display or reconnect remotely simply to check progress.

One automatic settled retry is permitted only when the chain itself identifies a calibration failure whose sole reason is the allowed clock-anchor condition. Any other retry requires the frozen cause-removal rule. With no named removable cause, the night ends.
