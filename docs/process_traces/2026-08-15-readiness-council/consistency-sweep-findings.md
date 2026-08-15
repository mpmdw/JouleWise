# Consistency sweep — findings only (span f99582e..HEAD 8937dec)

Scope: the span since the T6 session — PR #149 merge (`ac3fe1d`), the audit
baseline manifest (`694442c`), the T7 checkpoint + correction (`d279a7c`,
`8937dec`). READ-ONLY sweep; nothing applied. Repo left untouched
(audit baseline `ac3fe1d` intact; HEAD is 2 doc-only commits past it).

Verification method: every "current truth" cell below was checked against a
primary artifact (file bytes, `git log`/`git ls-tree`, recomputed sha256, or
`gh run list`), not against another doc's prose.

Counts: **7 blockers, 10 should-fix, 6 nits** (23 total).

---

## BLOCKERS (could mislead a successor — or an audit lens — into a wrong action)

### B1. `docs/phase_2/alpha_arm_readiness.md` is anchored at T4-late and asserts NO-GO for gates that have since closed — and contradicts itself

- **File:line:** `docs/phase_2/alpha_arm_readiness.md:9-11`, `:62`, `:67`, `:72`, `:73`, `:74`, `:75`, `:131`, `:134`, `:136`, `:139`, `:154`
- **Stale text:**
  - `:9-11` — "**Checkpoint:** T4-late, 2026-08-11 … **Current verdict: NO-GO. Do not arm Window ALPHA.**"
  - `:67` — "Arm-time identity-pin projection | **NO-GO — implemented and gauntlet-complete, merge in flight** … Awaiting CI green + the D-121 terminal review"
  - `:72` — "ALPHA campaign pack and extraction specification | **NO-GO.** U5 was not generated or hash-frozen at T1."
  - `:73` — "BETA and GAMMA pack family | **NO-GO.** U5–U7 were unfrozen."
  - `:74` — "Frozen readiness validator and record | **NO-GO.** … Phase B had not been reached at T1."
  - `:75` — "Reviewed measurement checkout | **NO-GO until the blocking merges finish.**"
  - `:62` — "Manual arming and recovery procedure | **GO for the document; PENDING for its live verification.**"
  - `:131` — "`desk.acceptance_owner` | NO-GO at the checkpoint: the copied-scalar removal was queued, not landed."
- **Current truth:** PR #131 merged 2026-08-12 (`14879e4` flipped D-131 to ADOPTED; council log C-057 §"What shipped"); all three packs FROZEN at `49dcc49` with D-134 freeze receipts PASS ×3 (`configs/campaigns/*/arm_readiness.freeze.receipts/freeze-0001.json`, `status: "PASS"`) and U11 projections frozen ×3; §5C **lead live verification discharged** (RUN_STATE.md:80-81, dry-run-0001, four hash-bound checks PASS); the reviewed measurement checkout **exists** at `/Users/edr/JouleWise-measurement-20260813` (verified on disk); CH-1/PR #142 landed the copied-scalar deletion — asserted in **this same file** at `:64` ("CH-1 deleted the writer's copied scalar"), directly contradicting `:131`.
- **Aggravating:** the file's own standing rule (`:3-6`) says "any checkpoint re-anchor of this document MUST resweep every gate row's status cell against main in the same commit — a banner-only re-anchor is the defect". The #149 span edited three cells in this file (M-2 note, `t0.*` rows) **without** re-anchoring or resweeping — the 4th occurrence of the fenced defect class.
- **Why blocker:** this is the "checked human view" of ALPHA arm readiness inside the pinned audit baseline. The PACK/READINESS/CUSTODY and AUTHORITY-PLANE lenses will read discharged rows as NOT-READY (false findings that consume the whole audit), or a successor reads "Current verdict: NO-GO" as the live verdict when the actual live gate is Ed's council directive.
- **Fix (one line):** re-anchor the header to T7/2026-08-14 and resweep every status cell against `ac3fe1d` in the same commit, per the file's own standing rule.

### B2. Three completed work orders are still written as OPEN in `TASK_QUEUE.md`, one of them "LAUNCH-BLOCKING"

- **File:line:** `TASK_QUEUE.md:659` (WO-ARM-EVIDENCE-AUTHOR-01), `:635` (WO-COLLECTION-MARGIN-01), `:201` (WO-MINT-ESTIMATOR-VOCAB)
- **Stale text:** `:659` "WO-ARM-EVIDENCE-AUTHOR-01 (registered 2026-08-13, T6; **LAUNCH-BLOCKING for any window night**) … Deadline: before the 2026-08-14 arm."; `:635` "Implementation in flight at registration"; `:201` "Priority: P2 (rises to P0 …) … Implementation stacks on impl/floor-commonmode-01 after round 9 lands."
- **Current truth:** WO-ARM-EVIDENCE-AUTHOR-01 shipped in #147, merged inside #149 `ac3fe1d` (`joulewise/arm_readiness_evidence_t0.py` +2043, `scripts/author_arm_evidence_t0.py`, `tests/test_arm_readiness_evidence_t0.py` +1566 in `git diff --stat f99582e..HEAD`); WO-COLLECTION-MARGIN-01 merged as #143 (RUN_STATE.md:88-89); WO-MINT-ESTIMATOR-VOCAB merged as #140 (RUN_STATE.md:87, C-057).
- **Why blocker:** the queue is the triage authority named in every intake rule. A successor (or the SEAMS/lifecycle lenses) reads a LAUNCH-BLOCKING open work order with a passed deadline and either re-implements it or reports the instrument NOT-READY.
- **Fix:** move all three to the Completed table with their PR/commit evidence and D-023-style closure cells.

### B3. WO-CI-RESTRUCTURE / D-130 closure is satisfied by evidence but recorded nowhere — deadline already breached in the docs' own terms

- **File:line:** `TASK_QUEUE.md:184-199`; `.github/workflows/d117-production-proof.yml:3-9`; `docs/phase_2/alpha_arm_readiness.md:63`; `docs/decision_log.md:155` (D-130)
- **Stale text:** `TASK_QUEUE.md:191-195` "Closure: the FIRST hosted green of the restructured workflow = the required second independent decisive execution (D-130) … **Deadline: before any claim publication and before the pack-freeze merge wave.**"; workflow header "ADVISORY pending D-130 closure … D-130 closure then flips this workflow back to automatic push/pull_request triggering" with `on: workflow_dispatch:` only.
- **Current truth:** the restructure merged as **#129** (2026-08-12 06:51Z, C-057) and the restructured workflow has **two hosted successes** — `gh run list --workflow=d117-production-proof.yml`: run **31541829071** `success`, 3h20m48s, 2026-08-11T22:18:21Z (this is the head-bound 23-job campaign RUN_STATE.md:326-328 already calls "D-130's second independent execution DISCHARGED") and run 31518739878 `success`. Meanwhile the **pack-freeze merge wave happened on 2026-08-13/14** — i.e. the stated deadline event has passed with no recorded disposition, and no doc records the closure either way.
- **Why blocker:** D-130's citation discipline for the paper ("never 'CI-proven decisive run'") and the workflow's trigger state both hang on this closure. Left ambiguous, either the paper under-cites its own strongest evidence or a successor over-cites it; and a "deadline breached without disposition" is exactly the shape the readiness council must rule on.
- **Fix:** record an explicit disposition — either "WO-CI-RESTRUCTURE CLOSED at run 31541829071 / #129, D-130 admission expired, citation discipline lifted, workflow re-triggered" or a written statement of what remains and why the freeze wave proceeded.

### B4. `docs/process/audit-baseline-manifest.json` pack digests reproduce under no algorithm and match no revision

- **File:line:** `docs/process/audit-baseline-manifest.json:23-27`
- **Stale/wrong text:** `"pack_digests": {"d117_contrast_…": "1cc0c784…", "d117_floor_qwen25_1p5b_v1": "f4c02c8a…", "d117_floor_qwen25_7b_v1": "6a8a3bf6…"}`
- **Current truth:** under the project's own canonical algorithm — `joulewise.committed_pack_tree_sha256.v1`, implemented in `tests/test_d117_floor_qwen25_1p5b_plan.py:230-236` and pinned at `:68` — the packs digest to `a0f05bd38fad325b4caa143123c5942b52b6295ec56716c8020b7d02e0a2322e` (1.5B), `04656cdad0a96a60…` (7B), `f340852c517e5e15…` (contrast) at both `ac3fe1d` and HEAD. I recomputed the manifest values under six candidate algorithms (rglob tree, git-tracked tree, path+space+sha, sha+2sp+path, concatenated binary digests, concatenated bytes, `git rev-parse HEAD:<pack>`) at revisions `49dcc49`, `ac3fe1d`, and HEAD: **zero matches**. The three manifest strings appear nowhere else in the repo. The manifest also names no digest algorithm.
- **Why blocker:** charter amendment 2 makes this manifest the immutable reference every lens cites and the basis for "any drift from it invalidates affected lens results". A pack digest that cannot be reproduced makes the drift check unrunnable — and a lens that *does* try to verify it gets a spurious mismatch on the frozen packs, the highest-severity finding shape in the audit.
- **Fix:** replace the three values with the canonical `committed_pack_tree_sha256.v1` digests above and add a `pack_digest_algorithm` field naming it.

### B5. The generated state kernel — declared the SOLE work-selection authority — is stale since 2026-08-08 and says no gates are active

- **File:line:** `docs/process/state_kernel.json` (`"updated": "2026-08-08"`); projections at `RUN_STATE.md:3414-3439` and `TASK_QUEUE.md:452-613`
- **Stale text:** `RUN_STATE.md:3419` "**Active Global Work-Selection Gates** — NONE — no global work-selection gate is active."; `:3427` "READY — Q2 `P2-006`: Homogeneous baselines (slice 2M) on the Mac target: **Window A two-model campaign**…" on the `[QUIET-MAC]` lane; `:3423` latest report = "T3 session 2026-08-09 day: … trust assembled, **PR #122 open** …".
- **Current truth:** PR #122 merged 2026-08-11 (`ae6af48`). A global gate **is** active: Ed's window-gating directive (`docs/decision_log.md:8847-8862`, 2026-08-13) — "do not focus on running the windows unless a COUNCIL decides the instruments are ready on a COMPREHENSIVE AUDIT" — plus the charter's council-READY requirement. The real next action is the eleven-seat fleet (RUN_STATE.md:25-36).
- **Why blocker:** README:7-9, PROJECT_STATUS.md:8-12, AGENT_PLAN.md (Superseded/WO-021 note) and TASK_QUEUE.md:410-414 all say work selection lives **only** in this generated region. A successor obeying that instruction is handed a six-day-stale selection whose top `[QUIET-MAC]` row is a *window campaign* — the exact action the live council gate forbids.
- **Fix:** update `docs/process/state_kernel.json` (council gate as an active global gate, current rows, current latest_report) and re-run `python3 scripts/gen_state.py`.

### B6. README activity blurb: "Queued next" still lists work that merged in #149, and calls the paused fleet "resumable"

- **File:line:** `README.md:12`, `:18-20`, `:26-33`
- **Stale text:** `:19-20` "the eleven-seat instrument-readiness audit was launched, then paused cleanly at a checkpoint (**resumable**; no results lost)"; `:26-28` "**Queued next:** (1) merge that tool after review; (2) a batch of small launch-procedure corrections found during packet assembly; (3) a comprehensive instrument-readiness audit …"
- **Current truth:** commit `8937dec` is the explicit correction — "fleet relaunches FRESH after /clear (resumeFromRunId is same-session-only …)", mirrored at RUN_STATE.md:25-32. Items (1) and (2) are the arm-time evidence author and the ten-item chain-fix batch, both merged in #149 `ac3fe1d` — the same blurb's own "Just completed" paragraph says so three lines earlier.
- **Why blocker:** the blurb is Ed's standing plain-language now/next surface; it currently self-contradicts within one screen and would send a reader (or a session driven off it) to re-merge landed work and to expect a resume that does not exist.
- **Fix:** rewrite "Queued next" to (1) relaunch the eleven-seat audit fresh, (2) refuter/cold-paired sitting + council verdict, (3) the batched Ed qualification session, (4) the three windows on GO, (5) paper fill — and drop "resumable".

### B7. The paper's mainline floor regime contradicts the frozen instrument, and the swap block has no live owner

- **File:line:** `docs/paper/draft-v1.md:114`, `:145`, `:208`, `:240`, `:250`, `:335-387` (the commented-out `CONDITIONAL-INSERT-TIGHTER-FLOOR` block)
- **Stale text:** `:114` "All comparative results issued in this cycle use the worst-case composition above … that conservative comparative false-effect floor is **8.611855 J**."; `:250` "The calculation nevertheless **is not consumed by any result issued this cycle because the floor-issuance path cannot yet select it** … the published path remains the conservative worst-case calculation."
- **Current truth:** D-133 cl.4's conditional **fired and was Ed-ratified**; all three packs are frozen at the **1.869502 J** two-shared-edge floor with `d124_two_shared_edge_common_mode.v1` selected in six shared-edge comparative cells (`docs/phase_2/alpha_arm_readiness.md:68`; RUN_STATE.md:74-76; freeze log `docs/process_traces/2026-08-13-freeze-execution/`). The stated blocker — "the floor-issuance path cannot yet select it" — was removed when WO-MINT-ESTIMATOR-VOCAB merged as #140. The 70h plan's own definition of DEFENSIBLE (`docs/strategy/2026-08-14-70h-plan.md:131-133`) gates every comparative claim on "its **1.869502 J** floor".
- **Aggravating:** the swap block is referenced **only** inside superseded RUN_STATE blocks (`:116`, `:140`, `:252`, `:322`) and two historical run reports — it appears in no live checkpoint, no queue row, and no plan item. It is an owed paper edit that has fallen out of every live surface.
- **Why blocker:** the first mint after ALPHA will produce verdicts against a 1.869502 J floor while the paper text says the published path is 8.611855 J and that the tighter method is unusable — a claim-bearing contradiction on the project's top-priority artifact.
- **Fix:** register the CONDITIONAL-INSERT-TIGHTER-FLOOR swap as a live queue row (P1, owner + trigger = first post-freeze mint) or execute the mechanical swap now.

---

## SHOULD-FIX

### S1. RUN_STATE "Last updated" line predates its own top checkpoint by three days
- `RUN_STATE.md:13` — "Last updated: 2026-08-12 (T6 session LIVE, Fable magistrate; window night TONIGHT per Ed ruling)". Truth: the top block is the T7 checkpoint of 2026-08-14/15 and no window night ran. **Fix:** "Last updated: 2026-08-14 (T7 checkpoint; fleet stopped, council gate pending)".

### S2. The baseline re-verification instruction is already arithmetically wrong
- `RUN_STATE.md:46-48` — "verify main still equals the baseline head + **this checkpoint commit** before resuming". Truth: HEAD is `8937dec`, i.e. **two** commits past `ac3fe1d` (`d279a7c` + `8937dec`), both doc-only. **Fix:** "…equals `ac3fe1d` plus the doc-only checkpoint commits `d279a7c`/`8937dec`; re-pin if anything else landed."

### S3. The decision log's M-2 remedy describes a regeneration that deliberately did not happen
- `docs/decision_log.md:8881-8893` — "Remedy: the chain-fix batch teaches the generators a freeze-aware status line … **and regenerates the sidecar-consistent text via the canonical path**; until that lands, the freeze receipt's presence governs". Truth: the shipped behavior is forward-only — `configs/campaigns/*/generate_configs.py` gained `freeze_aware_status()` but runs under `PRESERVE_CURRENT_FROZEN_BYTES`, so the frozen packs still read `"draft_status": "unfrozen_draft"` (`calibration_plan.json:3`) and "The pack is not armable." (`README.md:5`). That resolution is recorded in `docs/phase_2/alpha_arm_readiness.md:30-35` and RUN_STATE.md:55-56 but **not** in the policy home. **Fix:** append a one-line M-2 execution note: forward-only; the frozen packs' legacy wording is permanently overridden by the freeze receipt.

### S4. The baseline manifest is missing the chain-template sha the charter requires
- `docs/process/instrument-readiness-audit-charter.md:20-23` binds "the runbook + **chain-template** shas"; `docs/process/audit-baseline-manifest.json` carries `runbook_sha256` (verified correct: `25a4e809…` = `docs/phase_2/window_runbook.md`) and `freeze_manifest_sha256` (verified: `0ec66b66…` = `three_night_freeze_manifest.md`) but **no chain-template entry**. **Fix:** add the §6 chain-template artifact's sha (or state in the manifest that the chain template is the runbook §6 region covered by `runbook_sha256`).
- (Positive control: `row_registry_sha256`, `state_kernel_sha256`, `acceptance_artifact_sha256`, `runbook_sha256`, `freeze_manifest_sha256` all recomputed **MATCH** at HEAD.)

### S5. `PROJECT_STATUS.md` — the advisor doc — is two weeks behind
- `PROJECT_STATUS.md:373` (Update Ledger newest row = **2026-07-31**) and `:17-21` (newest body state = 2026-08-07 D-117). Missing: mint #1's D-110/D-113 disposition, the trust merge #122, the **first-ever three-pack FREEZE**, the tighter-floor adoption, and the council readiness gate. AGENT_PLAN.md:15-18 makes this refresh mandatory when a gate closes or a verdict lands. **Fix:** add 2026-08-05→08-14 ledger rows and a current-state paragraph naming the freeze + the council gate.

### S6. `CLAIMS_STATUS.md` has not moved since 2026-08-07 despite claim-bearing state changes
- `CLAIMS_STATUS.md:11` "Last updated: **2026-08-07**". Its own refresh rule (`:5-7`) triggers on "a verdict, a mint, a merge in the D-095 chain, an adjudication". Since then: D-133 cl.4 executed (tighter floor adopted), the estimator pre-registered in frozen packs, packs frozen, mint estimator vocabulary landed (#140). None appear. **Fix:** add a 2026-08-14 header noting the frozen packs, the pre-registered `d124_two_shared_edge_common_mode.v1`, and the 1.869502 J floor that will gate the prospective mints.

### S7. `WINDOW_STATUS.md` — README's named home for machine rules — omits every live machine rule
- `WINDOW_STATUS.md:1-7` (updated **2026-08-07**). Absent: do not dirty `/Users/edr/JouleWise-measurement-20260813`; **no reboot before T-0** (a reboot voids the frozen arm evidence — RUN_STATE.md:40-41, D-137 boot-session binding); no window may be armed before the council rules READY. **Fix:** add a three-line "current machine constraints" block mirroring RUN_STATE's T7 breath.

### S8. The landed T6 run report still carries its DRAFT/not-committed banner
- `docs/run_reports/2026-08-13-t6-session.md:3-7` — "**STATUS: DRAFT — mechanic-assembled, not landed, not committed.** … **Nothing in this file has been written into the repository.**" Truth: committed at `f99582e` with the magistrate attestation appended (`:1046+`). **Fix:** replace with "LANDED 2026-08-14 (`f99582e`); UNVERIFIED-BY-MECHANIC markers retained by convention".

### S9. The plan of record points a cold successor at the superseded checkpoint and a scratchpad that no longer matters
- `docs/strategy/2026-08-14-70h-plan.md:11-12` — "read RUN_STATE's **T6 checkpoint** first"; `:30-33` — "WO-ARM-EVIDENCE-AUTHOR-01: IMPLEMENTED overnight … **UNCOMMITTED** in scratchpad worktree wtARMAUTH … SALVAGE CLASS". Truth: T7 supersedes T6 and is the block a successor must read; the arm author is merged in `ac3fe1d`. Block 1 items 1-7 are all discharged, so "execute from the earliest incomplete item" now silently means Block 2/3. **Fix:** add a dated banner at `:1` — "STATE AT WRITING is historical; Block 1 CLOSED by #149; start at RUN_STATE's T7 block, then Block 2."

### S10. "All three packs FROZEN at 49dcc49" is true of the plan bytes but not of the pack trees
- `RUN_STATE.md:38-39`, `docs/strategy/2026-08-14-70h-plan.md:19-20`. Truth: `git diff --stat 49dcc49..HEAD -- configs/campaigns/` shows **374 insertions across all three packs' `generate_configs.py`** (the #149 freeze-aware generator work), so the committed pack trees differ from the freeze head (`324e9c97…` → `a0f05bd3…` for ALPHA). The freeze receipts bind `plan_sha256` (`2afabe98…`, unchanged) and the row registry, so nothing authorizing changed — but a custody lens diffing the pack tree against `49dcc49` will find a post-freeze delta with no note explaining it. **Fix:** add one clause — "frozen at 49dcc49; the pack generators were amended post-freeze under M-2 (#149) with frozen plan bytes and receipts preserved."

---

## NITS

### N1. Worktree count drifted
`RUN_STATE.md:20` "The **42** local worktrees … are ALL disposable." Actual: `git worktree list` returns 53 entries = main + **52** worktrees. **Fix:** say "~50 local worktrees (count with `git worktree list`)".

### N2. Ed-session duration disagrees across three docs
`docs/decision_log.md:8896` "ONE scripted **~15-minute** session" vs `docs/phase_2/ed-qualification-session.md:1` "one scripted visit (**~20 min**)" (steps sum to ~18 min) vs `RUN_STATE.md:68` "(**~20 min**)". **Fix:** make the decision-log line say ~20 min.

### N3. T7 header date is UTC, everything around it is PT
`RUN_STATE.md:15` "T7 CHECKPOINT (**2026-08-15**, Ed pause order)" while its commits are `2026-08-14 22:30 -0700`. **Fix:** "2026-08-14 PT / 2026-08-15Z".

### N4. README banner still describes the pre-U11 readiness path
`README.md:6-7` "Current work is the **U1-U10** readiness path followed by the prospective alpha, beta, and gamma claim windows." Truth: U11 exists and is frozen; current work is the eleven-seat readiness audit ahead of the windows. **Fix:** "the instrument-readiness audit followed by the prospective alpha/beta/gamma windows".

### N5. Supersession pointers inside RUN_STATE point backwards
`RUN_STATE.md:268` and `:272` — a T5-mid block and the 40-hour resume script both say "**SUPERSEDED by the T1 checkpoint (2026-08-08 night) below**", i.e. a later block superseded by an earlier one. **Fix:** point both at the T7 checkpoint above.

### N6. FLAKE occurrence count differs between the checkpoint and the queue row (the ONE home)
`RUN_STATE.md:63-64` "FLAKE-CALEXITS-311-REDERIVE fix shape registered not implemented (**4 occurrences**)" vs `TASK_QUEUE.md:615-634`, whose evidence names **2** (PR #143 run 31622634705; PR #144 18:31Z). Occurrences 3-4 (presumably in the #146-#149 arc) are unrecorded. **Fix:** add the two later occurrences with their run IDs to the queue row, or correct the checkpoint to 2.

---

## Checks that came back CLEAN (recorded so the next sweep need not redo them)

- Baseline manifest hashes `runbook_sha256`, `freeze_manifest_sha256`, `row_registry_sha256`, `acceptance_artifact_sha256`, `state_kernel_sha256` all recomputed **MATCH** at HEAD.
- Every path referenced by the T7 checkpoint **exists**: the Workflow fleet script (11,436 B, project dir — durability claim holds), `docs/phase_2/ed-qualification-session.md`, the charter + its consult trace, the freeze-execution log, the off-repo arm packet, the measurement checkout, and the staged `/tmp/ed-session/` scripts.
- The T6 merge count was correctly reconciled to **seven** (#140/#135/#141/#142/#143/#144/#145) in `RUN_STATE.md:87` and `70h-plan:24`, with #138 counted in T5 — the T6 report's owed correction (`:1084`) is discharged.
- Charter seat arithmetic is consistent: ten launch-gating + one non-gating = the "eleven-seat" fleet named in RUN_STATE and README.
- Window budgets agree across surfaces (~6.28 h / ~6.48 h ≈ README's "~6.3 / ~6.5 hours").
- D-136/D-137 renumbering is intact: exactly one D-136 (site retirement) and one D-137 (boot-session amendment) in `docs/decision_log.md`.

---

## MAGISTRATE VERIFICATION NOTE (appended post-sweep, 2026-08-14 T7 session)

**Blocker "pack_digests reproduce under no algorithm" is REFUTED — lead
live verification.** The manifest's three digests reproduce EXACTLY via
`joulewise.arm_readiness.committed_pack_tree_sha256` run in a worktree at
the baseline head ac3fe1d (and identically at PR #149's branch head
346ff4d):
- d117_floor_qwen25_1p5b_v1: f4c02c8a697c3a0db6b7b30a6a1f98808d233ee1d52f910241039cb6c0647f7c ✓
- d117_floor_qwen25_7b_v1: 6a8a3bf6527855bb7c189d48194336a...462e ✓ (full match)
- d117_contrast_qwen25_1p5b_vs_7b_v1: 1cc0c784...592d ✓ (full match)
Harness validated: the same procedure at the freeze head 49dcc49
reproduces the freeze-log digests (6246b618... / 1ef189a8... / 6a6865ae...),
which differ from ac3fe1d values because post-freeze commits (#146
registry reconciliation, #148/#149 M-2 freeze-aware status text, receipts
pinned into plan_tree) changed committed pack trees — expected, not drift.
The scout's claimed canonical values (a0f05bd3.../04656cda.../f340852c...)
match NO revision tested; its computation method was defective. The
manifest requires NO fix; the sweep's proposed remedy for this finding is
VOID. Remaining blockers (stale alpha_arm_readiness.md, stale state
kernel, B3/B7) stand as UNVERIFIED sweep findings for harvest triage.
