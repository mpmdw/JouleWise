# Docs-vs-truth audit — JouleWise main @ b81a2ac5 (2026-09-02 20:10 PDT)

Fresh read-only Fable seat, no loop context. Lens: "docs are context, code is
truth" (Ed 2026-09-01). Nothing edited; no git write commands; worktrees and
`/Users/edr/night-custody` untouched.

Evidence labels: **[exec]** = command run by this seat in this session
(output excerpted); **[seat]** = run by one of four read-only Opus sweep
seats this session and quoted verbatim (kernel-rows, ruled-not-installed,
process-docs, trace-pointers); the higher-ranked [seat] facts were re-run
[exec] before ranking and are so marked.

Ground truth used throughout [exec]:
- `git rev-parse --short HEAD` → `b81a2ac5`; `git status --short` → clean.
- `gh pr view 274 --json state,mergedAt,mergeCommit` → `MERGED
  2026-09-03T03:01:29Z b81a2ac5` (i.e. #274's merge IS the current head).
- `gh pr list --state merged --limit 40` → #273 (T26 items 1+4, e0f258ed),
  #275 (item 2, 33f61285), #274 (item 3, b81a2ac5), #272 (R7F fence),
  #276 (paper-d), #269 (projection-02), #267 (D-165 stage 2), #270/#271
  (paper a/b), #264/#265/#268 (night gate/driver/stage-2 fixes) all MERGED.
- `gh pr list --state open` → only #239 (fiducial, held).
- `python3 scripts/gen_state.py --check` → exit 0 (generated regions in
  TASK_QUEUE.md / RUN_STATE.md are byte-in-sync with the kernel JSON) [seat].
- Kernel: 129 live rows (queued 66, blocked 44, partial 11, shelved 7,
  active 1); `active_stop_card: null`; `updated: 2026-09-02`;
  `latest_report` → `docs/run_reports/2026-08-25-t23-t24-session.md`.
- `launchctl list | grep joulewise` → `com.joulewise.night` and
  `com.joulewise.night.deadman` loaded, exit 0; `date` → Wed Sep 2 20:06 PDT.
  rehearsal-20260903 is armed, not yet fired — NIGHT_HANDBACK is current.

---

## 1. Ranked corrections table

Rank = how badly a fresh reader (a new session, or Ed's advisor) is misled.
Tier A: a restarting session would ACT on it and be wrong. Tier B: advisor-
facing surfaces describe a different project. Tier C: internal retensing.

| # | Doc : line | Stale claim (short quote) | Contradicting evidence | One-line correction |
|---|---|---|---|---|
| **A1** | `RUN_STATE.md:13-17` (T30 header) | "A new session resumes from ONE file: `docs/process_traces/2026-09-02-decode-identity-set/39-pause-state-2026-09-02.md`" | [exec] `ls docs/process_traces/2026-09-02-decode-identity-set/` → `No such file or directory` on main. The file exists only on branch `fix/2026-09-02-decode-identity-set` (worktree `JouleWise-wt-decode-id`, head `2f3592c5`). Also contradicts the file's own rule at `RUN_STATE.md:9-11` ("Do not create another dated restart doc; update this file instead"). | Copy file 39 to main as a docs-only commit (or fold its "Resume sequence" and "Post-merge kernel batch" sections into the T30 block) and state the branch/worktree path explicitly. |
| **A2** | `RUN_STATE.md:19-22` | "T26 item 3 (#274) … needs only the peer notice + `gh pr ready` + `gh pr merge --merge`; do not add commits to that branch first." | [exec] `gh pr view 274` → `MERGED 2026-09-03T03:01:29Z`, merge commit `b81a2ac5` = HEAD. A resuming session following the T30 text would try to merge a merged PR. | Add a dated addendum: "#274 MERGED at b81a2ac5 (the head this file sits on); the post-merge kernel batch is now DUE." |
| **A3** | `docs/decision_log.md:216` + body `:10476-10480`; kernel `T26-RULING-INSTALL-01` = `partial` (TASK_QUEUE.md:617/758 "PARTIAL; READY; GATES close: D-170"); 9 rows carry a `pending` hard dep on D-170 | "D-170 … open (installs via T26-RULING-INSTALL-01)"; "moves to adopted only after all three installing pull requests land" | [exec] all three landed: #273 e0f258ed, #275 33f61285, #274 b81a2ac5. Mechanisms on main [exec]: `.github/pull_request_template.md`, `.github/workflows/gate-ledger.yml`, `joulewise/arm_readiness.py:6349 _T0_R1_TO_VALIDITY_ORIGIN_LIVENESS_NS = 600_000_000_000`, `docs/agent_playbook.md:57` M0 line, `tests/test_docs_freshness.py:140/364/581/639`, `docs/orchestration.md:82`. [exec] 9 rows still `pending` on D-170: GAMMA-UNIT-ROSTER-GUARD-01, L10-SACRIFICIAL-REHEARSAL-SCHEDULE-01, S9-01B/02/03/05/06, T26-RULING-INSTALL-01, V5-TRANSACTION-01. | Flip D-170 index+body to `adopted` naming #273/#274/#275; retire `T26-RULING-INSTALL-01`; mark the 9 deps `satisfied` with a `def test_` evidence pointer (D-170's own fence); `ED-BRANCH-PROTECTION-E1-01` (`TASK_QUEUE.md:585/716`, "BLOCKED — T26-RULING-INSTALL-01") → `queued` [ED-EXTERNAL]. |
| **A4** | `TASK_QUEUE.md:656/797` (kernel `V4-TRANSACTION-01` = `partial`, agent lane, "PARTIAL; READY [AGENT]") | "Execute the `_v4` family transaction per the FINAL r5 ruling … REMAINING SCOPE IS THE REAL TRANSACTION ONLY" | [exec] `docs/decision_log.md:210` (D-164): "`_v4` is never collected"; D-167 body (`:10434-10446`) installs `V5-TRANSACTION-01` "as the live successor to the retired Qwen2.5 Q2-Q4 windows"; kernel `V5-TRANSACTION-01` exists (`blocked`). A session picking "READY [AGENT]" rows would resume a transaction that will never run. Same stale premise in open PR #239's title "HOLD MERGE until `_v4` closes" [exec] while kernel `TRANSFER-FIDUCIAL-01` note says "Reconciled by D-167 … to the live `_v5` chain". | Retire `V4-TRANSACTION-01` by supersession (D-167 pattern used for WINDOW-COUNCIL-GATE), keeping its S-0 record as history in the status note; retitle #239. (Retiring a claim-path row is a magistrate call — record it as a D-167 addendum, not a silent kernel edit.) |
| **A5** | `TASK_QUEUE.md:601/737` (kernel `PIPELINE-SMOKE-LIVE-01`) | "BLOCKED — V5-QWEN3-PACK-GENERATED-S15 (… G2 waits on the S15 generator producing and freezing it)"; goal text still says "the W-11 desk tail on the REGENERATED `_v4` manifest" | [exec] kernel dump: dependency `kind: event`, `state: pending`, `target: V5-QWEN3-PACK-GENERATED-S15` — and that row is MISSING from the kernel (retired after #241 merged 2026-08-30). The dep can never be satisfied mechanically; the row is blocked on a ghost. The true remaining precondition is the freeze of the three `_v5` packs (owned by `V5-DECODE-IDENTITY-SET-01`, file 39 "live P-8 runbook freezing all three `_v5` packs"). | Retarget the dep to `V5-DECODE-IDENTITY-SET-01` (+ the pack-freeze event) and replace "`_v4` manifest" with "`_v5` pack" in the goal. |
| **A6** | `RUN_STATE.md:44-46` (T29) and `:70-72` (T28b); `PROJECT_STATUS.md:73,141` | "NEXT MACHINE STEP unchanged: G2-a evening → desk day → transaction ≈ 09-02/03"; "Next machine step: one instrumented evening, waiting on Ed." | [exec] no G2-a evening ran (kernel `V5-G2A-PREFILL-PROBE-01` = `queued`; no runs merged); the date has passed; D-169 (`decision_log.md:215`) put the unattended lane FIRST and `rehearsal-20260903` is the machine's next event (NIGHT_HANDBACK, launchd loaded). [exec] `grep -c -i "D-169\|unattended\|night driver\|rehearsal" PROJECT_STATUS.md` → 0. The `_v5` packs also cannot freeze until the decode-identity branch lands (file 39). | T30 block owns NEXT MACHINE STEP: rehearsal-20260903 harvest → stage-1 plan email → first DIAGNOSTIC_NO_PACK night → G2-a evening (date set by Ed's email reply), gated on the decode-identity merge + pack freeze. PROJECT_STATUS: one paragraph after `:141` naming the unattended driver and Ed's residue (single privileged install + GO). |
| **A7** | Rulings promising kernel rows that do not exist | `39-pause-state…:29` "Kernel row `LINEAGE-RELOCATABLE-01` goes into the post-merge kernel batch"; `docs/process_traces/2026-09-02-coldgate-r7f-unavailable/MAGISTRATE-RULING-r7f-unavailable.md:73` + `2026-09-02-dx-registry/MAGISTRATE-NOTES.md:27` "registered as a follow-up (kernel row `R7F-EXIT3-SEMANTICS-01`…)"; `2026-09-01-unattended/MAGISTRATE-RULING-UNATTENDED-STAGE1.md` R-12 "a separate small PR retargets the [`prewindow_check.sh --window`] pin"; D-170 body "Item 4's packet-input-list amendment is deferred to charter v3" | [exec] kernel lookup: `LINEAGE-RELOCATABLE-01 -> MISSING`, `R7F-EXIT3-SEMANTICS-01 -> MISSING` (#272 merged 20:17Z, batch never run). [exec] `scripts/prewindow_check.sh:51` still "the governed family is the `_v2` campaign packs" and no owner row (PREWINDOW-REGEX-01 covers only the regex [seat]). [seat] `grep -n "charter v3\|CHARTER-V3" state_kernel.json` → none; `grep -rn "artifact-pair exhibit\|Executed:" docs/contracts/bridge_protocol.md docs/orchestration.md docs/agent_playbook.md` → none. [exec] `NIGHT-REHEARSAL-01.acceptance` has 4 evidence rows; cold-gate d1 R-7 amendment (`coldgate-d1-RULING.md:118-121`) ruled a fifth (pre-night dead-man stand-down) — absent. | Register `LINEAGE-RELOCATABLE-01`, `R7F-EXIT3-SEMANTICS-01`, a `_v5` prewindow-pin row (or extend PREWINDOW-REGEX-01's acceptance), a charter-v3 owner row; add the fifth NIGHT-REHEARSAL-01 acceptance row. These are the 3rd–6th "ruled ≠ installed" instances since T26-RULING-INSTALL-01 was created to cure the pattern. |
| **A8** | Untracked work: `origin/feat/2026-09-02-paper-c` | (no doc mentions it) | [exec] `git log origin/main..origin/feat/2026-09-02-paper-c` → 2 commits (e2062735 "§11 references closed at 24 cited entries…", e1817fb8 fix round terra 177); no PR; `grep -rn "paper-c\|seat C" RUN_STATE.md` → nothing; no trace dir on main. Seats A/B/D landed as #270/#271/#276. | Open the paper-c PR (or register a kernel row) so the bibliography close is not lost at the pause. |
| **A9** | `TASK_QUEUE.md:665/806` (kernel `T0-UNATTENDED-01` = `partial`, "PARTIAL; READY [AGENT]"); `:666/807` `UNATTENDED-LAUNCH-01` "BLOCKED — T0-UNATTENDED-01" | Row reads as selectable work | [exec] its own status_note tail: "branch impl/t0-unattended-01 is content-identical to main … the remaining rehearsal-evaluator blockers are folded into the D-169 unattended lane and will be scheduled by that lane's staged ruling rather than as a separate PR." Status `partial` + agent lane makes it look READY. | Set `T0-UNATTENDED-01` to `blocked` on the D-169 stage-2 ruling (or absorb it into `UNATTENDED-LAUNCH-01`) so the queue view stops advertising it as READY. |
| **A10** | `docs/process/state_kernel.json` `latest_report`; `RUN_STATE.md:572` "Latest report: T23-T24 session 2026-08-24/25"; `docs/run_reports/README.md:13` "Read the latest report in this directory" | Points at 2026-08-25 | [exec] `ls docs/run_reports | tail -3` → last report 2026-08-25; sessions T25–T30 (~100 commits, 40 PRs since 08-28) have no run report; `docs/milestones.md:56-61` heartbeat fires at 14 days of silence (09-08) on the busiest fortnight in the project. | Either write one T25–T30 catch-up report and repoint `latest_report`, or amend the rule: the RUN_STATE T-block + the trace dir's pause file are the session record (and say so in `run_reports/README.md` and `milestones.md`). |
| **B1** | `README.md:12-22` ("**Status:**" paragraph, last touched 2026-08-20 per `git log -L`) | "the successor measurement campaign family is frozen … (2026-08-20) … The readiness re-audit and the plan for that next family are in progress" | [exec] D-164/165/166 (08-28) replaced that family with `_v5` (Qwen3 pair); #241 (08-30) merged the `_v5` pack prep; D-167 (09-01) reconciled the kernel; the night driver (#264/#265/#268) merged 09-02. The paragraph directly above the fresh "Current activity" blurb describes a campaign that was superseded 13 days ago. | Rewrite to: `_v5` Qwen3 campaign (D-164/165/166) designed and pack-prep merged; unattended night driver on main (D-169); packs freeze after the decode-identity fix; first instrumented night by Ed email approval. |
| **B2** | `README.md:75` | "Phase 1 is in its final stretch; **Phase 2's Mac vertical slice is complete**" | [exec] `docs/milestones.md` Phase table shows Phase 1 "Target end TBD"; `TASK_QUEUE.md:98` Completed items include every Phase-2 slice; the live work is a `_v5` claim campaign + paper (paper frozen at round 6, `RUN_STATE.md:127-129`). "Phase 1" as a frame is 2 months stale. | Replace the phase sentence with the campaign-state sentence; keep the 2026-07-06 live-path proof as history. |
| **B3** | `README.md:111,138-139` | "sequenced after Window A"; "Claim authority can arise only from the prospective alpha, beta, and gamma windows under D-117; the separately named Window C characterization night remains Ed ruling #1" | [exec] D-167 body: "Removed the retired Qwen2.5 `_v3` window rows `D117-W-ALPHA`, `D117-W-BETA`, and `D117-W-GAMMA`"; the live chain is G2-a → desk day → G2-b + `_v5` transaction → nightly G3. | "Claim authority arises only from the pre-registered `_v5` transaction nights (D-164–D-167) after G2-b"; drop Window A / Window C. |
| **B4** | `README.md:286-288`; `docs/publication_release_checklist.md:76-95` (step 6) | "sessions that change front-facing state refresh `docs/site/DRIFT.md`, and Ed deploys manually (D-068)" | [exec] `decision_log.md:180` D-136: "SITE LANE RETIRED FROM PROCESSES … no session spends tokens on Lakebed/capsule … manual dispatch only". Scripts and `site_capsule/` still exist [exec], so nothing is broken — but the README tells every session to do site work D-136 forbade. | Replace with "site lane retired (D-136); manual dispatch only, reference in the release checklist"; in the checklist mark step 6 "manual-dispatch reference, not a session step". |
| **B5** | `docs/publication_release_checklist.md:44-51` (step 3) | "regenerate the capstone artifacts from all six retained strict-valid bundles … `build_capstone.py --profile rpt001 --full`" | [seat] `decision_log.md` D-078 (accepted): "no claim-bearing extraction from time-anchor-defective powermetrics corpora"; `PROJECT_STATUS.md:187,258` those six bundles' energy values are VOIDED; the rpt001 profile still builds (`scripts/build_capstone.py:5-14`). The checklist as written produces a publishable-looking report from voided numbers. File age: last touched 2026-07-14 [exec]. | Add a D-078 fence at step 3: rpt001 six-bundle regeneration is plumbing evidence only, never claim-bearing; the publication corpus is the `_v5` transaction (uncollected). |
| **B6** | `docs/milestones.md` (whole file; last touched 2026-07-14 [exec]) | ":3 Status: skeleton - real dates pending user input (task P1-008)"; ":14 Supervisor approval meeting TBD"; ":15 3080 Ti borrow window … Phase 3 Stage 3.4"; ":28-39 Phase Targets all TBD" | [exec] `RUN_STATE.md:96-101` (T27c): advisor meeting pushed a week from 08-28 (≈09-04..07); kernel `P1-008` still `queued` since June; there is no Phase-3 hardware lane in the paper's answer set ([seat] `docs/research_question_coverage-2026-08-28.md:196`). The one calendar file has no `_v5` campaign calendar at all. | Rewrite as a live calendar: advisor meeting window, paper deadline, `_v5` sequence (rehearsal nights → G2-a → desk day → transaction → ~1 week collection → fills); demote the Phase 3–5 table to "historical plan skeleton". Keep the heartbeat rule but re-define "run report" (see A10). |
| **B7** | `docs/agent_playbook.md:34-46, 93-469` | Mission menu "ungated, any time: M1 (Slice 2N) … M7 (2I Mac slice — the flagship)"; `:449` handoff to `docs/phase_2/baseline_results.md` | [seat] P0-002/P2-003/P2-007/P2-009/P2-025/P3-001 all under `TASK_QUEUE.md:98 ## Completed Queue Items`, none in the kernel; [exec] `ls docs/phase_2/baseline_results.md` → No such file. M4 "Close D-016" is superseded by D-164 (`decision_log.md:60` still shows D-016 `open`). M0 (`:50-92`) IS current (D-170 line at :57). README:243 sends every "next step" agent here first. | Keep M0; demote M1–M10 to a "Historical missions (all closed 2026-07)" section with a live pointer to the kernel's `_v5` rows; fix the dead pointer; mark D-016 superseded by D-164. |
| **B8** | `docs/orchestration.md:12-47, 266-309` | ":23 The designated lead owns decomposition, triage, design adjudication, every final diff gate"; ":266-284 Topology: how it evolved — v1 (2026-07-07 AM) … v2 …" | [seat] `grep -c "magistrate\|lieutenant\|cold gate" docs/orchestration.md` → 1; the live topology (rule 11: magistrate / lieutenant / cold gate, three-seat consult, standing escalation trigger) is encoded in `.github/pull_request_template.md:20` and CLAUDE.local.md but not in the repo's only in-tree process description. | Add a Roles section for rule 11 (what the lieutenant may not decide, cold-gate triggers); demote `:266-309` to historical. |
| **B9** | `docs/risk_register.md:48-53, 228-236, 305-332` | R-001 "all work since has been hardware-independent … Slice 2N is next"; R-012 descope ladder rungs 1–4 (live split, Orin/Pi…); R-016 iCloud backup live vs R-017 "never under iCloud" | [seat] real M3 Max powermetrics bundles since 2026-07-06 (`PROJECT_STATUS.md:258`); every ladder rung above the floor is already out of scope by design; R-016/R-017 read as contradictory to a fresh reader. No row covers the two live top risks (unattended nights with Ed absent, D-169; the paper deadline). | Restate R-001 as the advisor-scope risk; replace the ladder with the `_v5` descope ladder (D-166 refusal branch, D-165 dominance-sentence withdrawal); one sentence separating backup copy (iCloud, sanctioned) from live corpus (never synced); add R-021 unattended-night and R-022 paper-deadline rows. |
| **B10** | `PROJECT_STATUS.md:136` | "(close-out decision D-168). A" | [seat] dangling fragment left by the #253 reconcile, in the advisor's first-screen read. | Delete the orphan "A". |
| **C1** | `RUN_STATE.md:35-42` (T29) | "FRESH-MODEL REPO REVIEW IN FLIGHT … the magistrate synthesis + 'would change' disposition follows there"; ":42 17 worktrees hold squash-merged branches" | [exec] `docs/process_traces/2026-09-01-fresh-model-review/00-MAGISTRATE-SYNTHESIS.md` exists (all four seat reports + addendum [seat]); [exec] `git worktree list \| wc -l` → 43 entries (main + 42 linked; 15 detached). | Retense T29: review CLOSED at 00-MAGISTRATE-SYNTHESIS.md; re-derive the removal list for Ed from `git worktree list` at resume. |
| **C2** | `docs/decision_log.md` D-131 amendment | kernel `V5-DECODE-IDENTITY-SET-01` note: "D-131 cl.2/cl.3 amendment text (R-7) is owed to the decision log at the bench" | [seat] `grep -n "D-131" docs/decision_log.md \| grep -i "amend\|2026-09-02\|R-7"` → none; `docs/contracts/d165_dominance_closeout.md:61` still `cell-prefill_p256-a/-b`. Genuinely owed (in flight on the decode-identity branch) — listed so the pause cannot drop it. | Hang it off the decode-identity landing checklist (file 39 resume sequence). |
| **C3** | Trace retenses (all [seat], PRs verified merged) | `2026-09-02-t26-item-3/MAGISTRATE-NOTES.md:17` "NOT YET APPLIED"; `2026-09-02-paper-d-dg071/MAGISTRATE-NOTES.md:131-137` "after `feat/2026-09-02-dx-registry` merges"; `2026-09-02-process-rules/MAGISTRATE-RULING-process-rules.md:119` "in-flight T26 install branch"; kernel `SUPERSESSION-CROSS-CONSUMER-DIVERGENCE-01` "luna delta re-audit of r7 in flight" (#260 merged); kernel `V5-DECODE-IDENTITY-SET-01` note "Sol xhigh implementation seat in flight … red test first" (branch is 3 fix rounds further); `fresh-model-review/00-MAGISTRATE-SYNTHESIS.md:50` "PROJECT_STATUS still owed" (#253 merged) | Each precondition is met on main. The paper-d follow-ups (registry rows DG-071/075 on the bench registry, rendered-digit disclosure row, scratchpad-path redactions) are now DUE, not deferred. | One retense pass; the DUE items join the post-merge kernel batch. |
| **C4** | `2026-09-02-coldgate-dx-t26a/MAGISTRATE-RULING-coldgate-dx-t26a.md` A1 item 4 | Acceptance predicate: "`grep -n 'Decimal(str(\|float(' scripts/check_paper_round7_artifacts.py` is empty" | [seat] 6 hits remain (`:595` tolerance arithmetic, `:629-635` SVG geometry) while the substantive cure IS installed (`:369/:815 parse_float=Decimal`, `:417 _typed`, `:197`). The ruled acceptance grep can never be empty while tolerance arithmetic exists. | Dated addendum excluding `_geometry`/SVG-attribute sites from the predicate (same form as the existing :565→:597 addendum, commit 403998e1). |
| **C5** | `2026-09-02-paper-d-dg071/41-coldgate-opus-refutation-fixture-shape.md:75,158` | cites commit `fb601e54…` | [seat] `git cat-file -t fb601e540240…` → "could not get object info" (a throwaway-repo experiment sha, reads as a repo commit). Only unresolvable sha across 12 trace dirs; every PR number resolves. | Label it "throwaway-repo sha, not a JouleWise commit". |
| **C6** | `TASK_QUEUE.md:6-33` intake rule; `docs/council_log.md` | Categories "Phase 1 evidence work / Phase 2 implementation prep"; council log's last block is T29 (`:3897`) — no T30 entry (T30 had two cold gates: dx-t26a, r7f-unavailable, process-rules) | [exec] `grep -n "^## " docs/council_log.md \| tail -1` → T29. | Add the T30 council-log block at resume; retire the phase vocabulary in the intake rule. |

## 2. Soundness fences — KEEP even though old (do not "reconcile" these)

- D-078 voiding language in `README.md:82-88, 155-175` and everywhere the
  six-bundle / nine-bundle corpora appear; the checklist's step-3 fix (B5)
  ADDS a fence, it does not soften one.
- `docs/publication_release_checklist.md:11-19` boundary table (release +
  Lakebed credentials Ed-only; fixture smoke ≠ corpus evidence; `--dry-run`
  is not a preview).
- `docs/risk_register.md:263-277` R-015 (bundles are evidence, never edited
  in place), `:279-317` R-016 corpus preservation, `:366-409` R-019/R-020
  registered residuals with reopening triggers (pre-registration record).
- `docs/research_question_registry.md` `forbidden_upgrade` column and
  `:119-135` attribution limits (C-014/C-015) — the registry is otherwise
  CLEAN (zero `_v4`/Window-A hits; DG-071/075 live in
  `docs/paper/results-fill-registry.md:643,647,908`, not the registry, and
  that is correct).
- `docs/orchestration.md:215-264` spend guardrails (Ed-owned bands).
- Kernel fences on `V5-TRANSACTION-01` (D-078 no-retry, D-149 T-0
  conditions) and the D-170 item-3 "liveness bound, not metrology" fence.
- D-127 §2 zero-agent capture fence and the night gate's
  `night_refused_agent_present` refusal (verified installed [seat]).

## 3. Minimal reconciliation plan (no edits performed)

Order matters: step 0 is a 15-line docs commit that stops the next session
from mis-resuming; step 1 is the kernel batch the pause file already
enumerates; steps 2–4 are the advisor surfaces and the July skeletons.

**Step 0 — `RUN_STATE.md` T30 addendum (bench, docs-only commit to main,
before anything else).** (A1, A2, A6, C1)
1. Dated addendum under T30: "#274 MERGED at `b81a2ac5`; post-merge kernel
   batch DUE."
2. Resume-file pointer: name the branch + worktree, or commit file 39 (and
   40) to main under `docs/process_traces/2026-09-02-decode-identity-set/`
   as a docs-only cherry-pick — the latter also honours `RUN_STATE.md:9-11`.
3. Replace T29's "NEXT MACHINE STEP unchanged" with the T30 sequence:
   rehearsal-20260903 harvest → stage-1 plan email → first DIAGNOSTIC_NO_PACK
   night → G2-a evening (Ed-emailed date), all gated on decode-identity
   merge + `_v5` pack freeze. Retense T29's review to CLOSED.
4. Add the T30 block to `docs/council_log.md` (C6).

**Step 1 — the post-merge kernel batch (`docs/process/state_kernel.json`
then `python3 scripts/gen_state.py`; verify with `--check` and
`python3 -m unittest tests.test_docs_freshness tests.test_gen_state`).**
(A3, A4, A5, A7, A9, A10, C3)
1. D-170 → `adopted` naming #273/#274/#275 (index `:216` + body
   `:10478`); satisfy the 9 pending D-170 deps with a `def test_` pointer;
   retire `T26-RULING-INSTALL-01`; `ED-BRANCH-PROTECTION-E1-01` → `queued`.
2. Register: `LINEAGE-RELOCATABLE-01`, `R7F-EXIT3-SEMANTICS-01`, the
   `_v5` prewindow-pin retarget (or extend `PREWINDOW-REGEX-01`), a
   charter-v3 owner for D-170 item 4's deferral, the rendered-digit
   disclosure row; fifth `NIGHT-REHEARSAL-01` acceptance row + status-note
   refresh (item 1 MET, 20260902 delivered, 20260903 armed).
3. `PIPELINE-SMOKE-LIVE-01`: retarget the ghost dep to
   `V5-DECODE-IDENTITY-SET-01` + pack-freeze event; `_v4`→`_v5` in goal.
4. `T0-UNATTENDED-01` → `blocked` on the D-169 stage-2 ruling.
5. `V4-TRANSACTION-01` → retire by supersession with a D-167 dated
   addendum (magistrate ruling, keep the S-0 record as history); retitle
   PR #239.
6. `latest_report`: write `docs/run_reports/2026-09-02-t25-t30-session.md`
   (or repoint to the T30 block and amend `run_reports/README.md`).
7. Open the paper-c PR or register its row (A8).

**Step 2 — advisor surfaces (`README.md`, `PROJECT_STATUS.md`).** (B1–B4,
B10, A6)
1. README `:12-22` Status paragraph → `_v5` + unattended state; `:75`
   phase sentence → campaign sentence; `:111,138-139` → `_v5` transaction
   nights; `:286-288` → D-136 wording. Keep the D-078 paragraphs verbatim.
2. PROJECT_STATUS: unattended-lane paragraph after `:141`; delete the
   orphan "A" at `:136`.

**Step 3 — the July skeletons.** (B5–B9)
1. `docs/milestones.md`: rewrite as the live calendar; Phase 3–5 table →
   historical; heartbeat rule re-defined.
2. `docs/publication_release_checklist.md`: D-078 fence at step 3; step 6
   marked manual-dispatch reference (D-136).
3. `docs/agent_playbook.md`: keep M0; M1–M10 → historical section; fix
   `:449`; D-016 → superseded by D-164 (also `decision_log.md:60`).
4. `docs/orchestration.md`: rule-11 Roles section; `:266-309` historical.
5. `docs/risk_register.md`: R-001/R-012/R-016-17 restated; add
   unattended-night and paper-deadline rows.

**Step 4 — trace retenses (docs-only, one commit).** (C2–C5)
Retense the six "in flight / not yet applied / after X merges" lines to
their landed state; dated addendum on dx-t26a A1 item 4; label the
throwaway sha; carry the D-131 amendment on the decode-identity landing
checklist.

Verification after each step: `python3 scripts/gen_state.py --check`,
`python3 -m unittest tests.test_docs_freshness tests.test_gen_state`, and
`git diff --stat` limited to the files named above.

## 4. Seat reports consumed (for custody)

Four read-only Opus sweeps this session: kernel-rows-vs-git, ruled-not-
installed (D-160–D-171 + 12 trace dirs; D-157/D-158 confirmed INSTALLED,
D-170 items 1–3 INSTALLED), process-doc staleness (7 files), trace-pointer
staleness (12 dirs + NIGHT_HANDBACK/COURIER; all 17 cited PRs MERGED). Their
[seat] evidence is quoted with the command; the A-tier facts were re-run
[exec] by this seat before ranking.
