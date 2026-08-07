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
session id: 019fddaa-39a2-7b00-8cdc-d4842dd28993
--------
user
IMPLEMENTATION-PLAN DRAFT — U4: synthetic three-window live-ledger regression (read-only; no writes; final message = the plan). Source: docs/process_traces/2026-08-07-d117-plan-freeze/DESIGN-MEMO.md §'Synthetic three-window live-ledger regression' (the fixture semantics, the no-failure extension, the proof obligations, the full refusal-vector list) + the U4 row in the work-order table + the landed U1 branch impl/d117-u1-ledger-session (fetch origin and read its diff for the session-capability API shapes you must exercise) + U2's pending successor engine (design brief forthcoming — mark successor-dependent vectors as staged behind U2). Draft the COMPLETE implementation plan: exact WRITE_SCOPE files; fixture-construction algorithm (76-receipt issuance semantics + 3 session capabilities + 6 finalized live observations); every proof obligation as a named test; every refusal vector as a named test with its setup; which tests are blocked on U2 and how to stage them (skip-marked vs separate module); estimated size; risks; open questions for the lead. Plan quality bar: an implementer should be able to execute it without further design decisions.
codex
I’ll trace the governing memo, queue/state, orchestration rules, and the landed U1 branch API before drafting. This is a read-only planning pass; I won’t modify the workspace.
exec
/bin/zsh -lc 'git status --short --branch && rg -n "ACTIVE_STOP_CARD|Current Project Status|Known Workspace State|What Is Next" RUN_STATE.md && rg -n "Current Queue|Do-Not-Do-Yet|U4|D117|three-window|live-ledger" TASK_QUEUE.md && rg -n "Mission M0|M0" docs/agent_playbook.md && rg -n "delegat|review|multi-stream|plan|write scope|D-050" docs/orchestration.md' in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
## main...origin/main
2008:12. If an `ACTIVE_STOP_CARD` exists below, it overrides every normal
2043:## ACTIVE_STOP_CARD
2182:## Current Project Status
2743:## Known Workspace State
96:Current Queue region is the sole live work-selection view.
213:## Current Do-Not-Do-Yet List
306:## Current Queue
26:1. Run Mission M0 (preflight) — always.
50:## Mission M0: Preflight (every session)
472:The M0 step-6 handoff list, plus: if you changed an adapter or bundle
12:## Roles: a lead, independent implementers/reviewers, and a human at the top
22:  2026-07-08 once the review gate had proven itself).
28:- **Independent implementation and review agents** do the heavy reading and
29:  writing: implementation against pinned specs, adversarial review
31:  fresh instance audits), docs drafting, and review of the lead's own
32:  consequential decisions. Cross-model review is load-bearing by
39:- **Image-heavy analysis uses the designated image-capable review route** per
54:   assign each stream a review tier by *cost of being wrong*
60:3. **Per-stream pipeline** — for each reviewable unit: an invited
62:   coding), implementation, then a layered review stack:
63:   2–3 fresh-instance counterreview lenses over the diff → lead triage
66:   writer≠reviewer test audit (a fresh instance hunts tautological,
68:4. **Lead live gates** — never delegated: the lead runs the real flow
74:   merge: a pre-merge oversight pass by 2–3 fresh reviewers with
78:   review round gets one more fresh review before merge — no commit
79:   merges unreviewed, however small (its first application caught a
80:   crash path in a "trivial" post-review fix).
81:6. **Integration review** — after parallel streams merge, one dedicated
82:   review hunts *interaction* defects no single-stream review can see.
86:   refreshed; a delegated docs-consistency sweep before the final
102:10. **Meta-review (the final step)** — event-driven, not calendar-driven:
103:    when a review layer stops earning its keep, when an intervention
105:    reviewed with its own evidence discipline (see Topology for the
106:    consensus one such review produced). After large workloads the
132:| `LEAD_GATED` | The lead has reviewed and run the required local/live checks for the item. |
149:| `docs/council_log.md` | The deliberation record: review-council positions, reasoning exchanged, who prevailed, overridden dissents — so a future reader can reconstruct *why*, not just *what*. The log is the range/count authority. |
150:| `docs/contracts/` | Claim/evidence contracts: `claims_ladder.md` (D-037) plus `analysis_plans.md` (D-038) form the claim gate; strict validation is the evidence ticket. |
152:| `docs/run_reports/` | One record per working session: outcomes, verification evidence, a per-layer catch/yield table, the delegation-calibration ledger, restart instructions. |
160:- **Per-layer yield:** every review layer's unique catches are
162:  earlier two-zero-sessions auto-drop, which the integration-review
168:  TRIGGER an expected-loss review decision, never automatic deletion;
170:  zero-defect streaks. (One layer, the default specialist review lens, was
172:- **Delegation calibration:** every delegated unit gets a row — task
177:  vibes. Current signal: pinned-spec delegation runs essentially
180:- **Invocation manifest:** substantial delegated/tool/skill runs get a
213:audit work order WO-022 (`docs/reviews/2026-07-13-comprehensive-audit/`).
215:SPEND GUARDRAILS (capstone benchmark bands) — provisional calibration constants; review after two completed arcs; sunset at capstone submission.
221:3. BOUNDARIES AND ATTRIBUTION. An arc = one council-log C-row, opened at its first delegated session, closed at its closeout snapshot. A work order = one WO/task id. Failed calls, retries, resumes, refuters, fix rounds, delta re-audits, lead usage, and subagents all count against the initiating WO and arc. Arcs and WOs may not be split, renamed, or reopened to reset counters.
223:4. BANDS. Each dimension is independent. SOFT crossing = record-and-continue: flag in the spend snapshot plus a one-line justification in the council row. HARD crossing = pause-and-ask Ed before any NEW delegated work in that category; in-flight sessions finish; quiet-machine measurement is never interrupted.
238:5. CHECKPOINTS (procedural; owner = the Fable lead). (a) At arc open: predeclare one accepted deliverable increment for the arc — a corpus/measurement result, analysis/figure/report increment, evaluator requirement, or cited advancement of a D-060 gate — and classify planned delegated work as deliverable-facing or process-facing (mixed sessions count as process-facing unless separately attributable). (b) Before each next delegated call: check the completed session against its tier band (a lightweight glance, not a full snapshot); no runtime killing is promised — evaluation happens on completed sessions before any resume, replacement, or new call. (c) At WO close and arc close: take the spend snapshot and evaluate all bands. One missed checkpoint blocks new process-facing delegation until reconciled.
240:6. DELIVERABLE-PROGRESS TRIPWIRE (binds while ANY D-060 gate is unmet). If process-facing combined estimated cost exceeds 33% of arc cost OR $250 — whichever occurs first — HARD pause-and-ask Ed before further process-facing delegation. Independently, an arc that closes with process-facing spend but NO accepted deliverable increment pauses further non-exempt process work even if the 33% threshold was not crossed.
246:9. KEEP-DEFENDER GUARANTEE. No cap consequence auto-deletes a review layer. Layers with recorded unique catches survive any cap; a cap response batches, rescopes, or seeks Ed approval — never silently drops catch-bearing gates (final-head, integration, lead-live, claim/evidence safeguards).
250:11. RECALIBRATION AND OWNERSHIP. Band values are calibration constants: the lead may amend SOFT values at arc close with evidence via a one-line decision-log amendment; HARD values and this section's structure are Ed-owned. Scheduled review after two completed arcs. The whole policy sunsets at capstone submission.
257:it (docs/reviews/2026-07-13-comprehensive-audit/receipts/
270:- **Meta-review (C-009):** a signed cross-model consensus — two blind
282:review of the lead's process schemas rejected two of them and supplied
283:better ones (now the v2 ledger and calibration formats), and review
294:complete fixture-first NVIDIA stack. The layered review recorded, among
300:caught only by the post-merge integration review, and a crash path
303:delegated Codex sessions; the lead never wrote implementation code and
323:  `codex-delegation` is the invocation/consumption contract,
324:  `adversarial-review` defines refutation tiers,
325:  `multi-stream-worktrees` defines parallel stream mechanics,
330:  analysis-plans contracts give claim gating; `docs/stream_logs/` and
334:- Skill-only: exact conductor sequencing, delegated-agent prompt/consumption

exec
/bin/zsh -lc "sed -n '50,125p' docs/agent_playbook.md; sed -n '2043,2088p' RUN_STATE.md; sed -n '2182,2248p' RUN_STATE.md; sed -n '2743,2815p' RUN_STATE.md; sed -n '306,405p' TASK_QUEUE.md; sed -n '213,305p' TASK_QUEUE.md; sed -n '1,210p' docs/orchestration.md; rg -n \"Synthetic three-window live-ledger regression|U4|work-order|76|successor|refusal|no-failure|proof obligation\" docs/process_traces/2026-08-07-d117-plan-freeze/DESIGN-MEMO.md" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
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

## Mission M1: Slice 2N — Pre-Hardware Hardening (queue P2-007)

**Gate:** none. **Spec + acceptance:** `docs/phase_2/phase_2_plan.md`
Slice 2N. This mission adds the code-level route for each work item,
sourced from the 2026-07-05 external code review. Line numbers are from
commit `ae48abe` — re-locate by symbol name if the files have moved on.

Read first: `phase_2_plan.md` Slice 2N + Cross-Slice Contracts;
`joulewise/bundle.py`, `controller.py`, `reduce.py`, `interfaces.py`
(skim whole files — they are small and the invariants interlock).

2N is one mission but NOT one sitting: it touches adapter interfaces,
controller timing, reducer behavior, report parsing, CLI, schema export,
and validation policy. Work item-by-item with the suite green after each,
and land it as roughly three commits so a failure bisects cleanly:

- **Commit A — the adapter seam:** 2N.1 (RunContext + raw evidence),
  2N.2 (measured-window boundaries). Both touch controller/interfaces.
- **Commit B — the read layer:** 2N.8 (BundleReader), with 2N.4 (rail
  contract), 2N.7 (report alignment), and 2N.6's structured read
  failures implemented on top of it. 2N.6's CLI verb rides along.
- **Commit C — schema + metrics:** 2N.5 (schema round-trip), 2N.3
  (token-count fallback), 2N.9 (v0.2 compatibility note).

If a session ends mid-slice, a completed commit group is a clean
handoff point — say which group landed in `RUN_STATE.md`.

Per-item detail (each item = tests green before the next; items 1+2
change the controller/adapter contract and go first):

### 2N.1 `RunContext` seam + raw evidence

- Today: `RunBundleWriter._ensure_layout` creates `raw/` (bundle.py
  ~line 160) but no method writes into it, and adapters never see the
  bundle path — so a real telemetry adapter cannot honor D-002 ("raw
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
7:  "summary": "Complete D-117 freeze design: three prospective windows fit the envelope, but live-ledger sessions, multi-cell minting, and D-102 successor generation must land before any arm.",
11:    "head_start": "dbb9685669ac76ea65bf458b78eeb98d94bc6a80",
37:        "title": "No usable D-102 successor-artifact path exists for a live-prefixed ledger",
39:        "recommendation": "Pre-build and cold-gate a deterministic successor builder, registry, live-prefix verification, and trigger-time operator procedure."
131:Ideal no-failure receipt evolution from the issued sequence-76 head is three receipts per window—session capability, pre finalization, post finalization—ending at sequence 85 after all three windows. Exact sequence numbers are arm-time facts, not desk-frozen plan literals.
153:### F3 — The D-102 successor packet is a pre-arm dependency (blocker)
157:- deterministic successor builder and validator;
161:- a dry-run fixture that produces exact successor bytes and expected head pin;
162:- trigger-disposition logic that judges the range-expanding observation under the prior artifact before incorporating it into the successor;
165:I recommend deriving a successor from all content-distinct, valid, same-epoch observations through the chosen cutoff. Systematic, ordinary-invalid, aborted, or unresolved attempts remain recorded but excluded. The lead should explicitly ratify that corpus rule because D-102 establishes the successor obligation but does not fully spell out this live-prefix derivation policy.
167:At the pre bookend, a range expansion stops the chain before member one: close or preserve the bracket session according to the frozen state machine, commit the current ledger head, build and authenticate the successor, revalidate, then proceed. A post range expansion follows the same process after science but before the verdict. Systematic mismatch is a refusal, never something a successor can launder.
230:- ordered stage records with exact stage-manifest ID, SHA, expected member count, predecessor, and successor;
405:### Synthetic three-window live-ledger regression
407:The fixture begins with the exact issued-ledger semantics: 76 receipts, including 38 historical import observations—30 valid, 2 systematic, 6 ordinary-invalid. Candidate discovery must exclude every import-marked observation.
409:The no-failure live extension adds three bracket capabilities and six finalized live observations. From one immutable final snapshot, the regression must prove:
419:Required refusal vectors:
429:- one range-expanding live observation requiring a successor;
431:- a successor whose prior set omits or changes an authenticated prefix.
443:1. **Ruling gate:** lead accepts the session-capability semantics, zero-retry policy, successor corpus rule, four-cell artifact shape, and fourth-window treatment.
444:2. **Toolchain gate:** ledger session/binding, successor builder, pinset v2, multi-cell mint, prefill metric support, and three-window regression all land and pass focused plus canonical suites.
447:5. **Pre-science trigger gate:** finalize the pre observation and either accept it, issue a governed successor, or abort before member one.
456:| U1 — ledger session and binding | `joulewise/calibration_ledger.py`; `joulewise/calibration_bracketing.py`; `scripts/reserve_calibration_window_bracket.py`; `tests/test_calibration_ledger.py`; `tests/test_calibration_bracketing.py` | Two immutable slots, one-use finalization, governed abort, no unresolved-candidate leakage, exact binding, head/pin refusals. Focused ledger/bracketing tests plus full suite. | Foundation; independent of U3 |
457:| U2 — D-102 successor engine | `joulewise/calibration_bracketing.py`; `scripts/build_calibration_acceptance_successor.py`; `configs/calibration/calibration_acceptance_registry.json`; `tests/test_calibration_acceptance_successor.py` | Complete authenticated live prefix, deterministic bytes, parent ancestry, exact Decimal derivation, range/count triggers, systematic refusal. Focused cold-gate fixtures plus full suite. | Sequential after U1 because of shared bracketing semantics |
458:| U3 — pinset v2 and multi-cell mint | `scripts/mint_floor_artifact_generalized.py`; `scripts/floor_mint_pinsets/schema_v2.json`; `joulewise/detection_floor.py`; `tests/test_mint_floor_artifact_generalized.py` | Decode and prefill metrics, per-plan component pins, aggregate four-cell pins, no derived literals, no cross-stack sum, v1 compatibility. Focused parity/refusal tests plus full suite. | Independent of U1/U2 |
459:| U4 — three-window ledger regression | `tests/fixtures/calibration_live_three_window/**`; `tests/test_calibration_live_three_window.py` | Exact issuance fixture, import exclusion, six live candidates, three causal bindings, successor and refusal vectors. | After U1 and U2 |
463:| U8 — operator/readiness packet | `docs/phase_2/window_runbook.md`; `scripts/validate_frozen_plan_readiness.py`; `tests/test_frozen_plan_readiness.py` | §5A sequence, session capability, pre-trigger successor gate, fresh roots, empty waivers, terminal binding/pin/backup. | After U1, U2, U5–U7 |
472:- Ratify the two-slot ledger capability against D-109/D-116, especially whether an open post slot may exist during the pre-science successor probe.
474:- Ratify the D-102 successor corpus rule: all content-distinct valid same-epoch observations through the cutoff.
488:No live timings, calibration observations, successor generation, or mint replay were performed. Runtime estimates therefore inherit historical-machine variance; the 20% margin is the current mitigation.

codex
The stop card is clear, and U4 is explicitly downstream of U1/U2. I’m narrowing now to the memo’s normative fixture/refusal text and the exact U1 public API surfaces, including whether the requested origin branch is already present locally so I can honor the no-write constraint.
exec
/bin/zsh -lc "sed -n '100,180p' docs/process_traces/2026-08-07-d117-plan-freeze/DESIGN-MEMO.md; sed -n '390,440p' docs/process_traces/2026-08-07-d117-plan-freeze/DESIGN-MEMO.md; sed -n '440,490p' docs/process_traces/2026-08-07-d117-plan-freeze/DESIGN-MEMO.md; git branch -a --list '*d117*' '*u1*' '*u2*'; git show-ref | rg 'impl/d117-u1-ledger-session|d117-u1' || true; git remote -v" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
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

The absent feasibility synthesis limits review of the optional 256-token arm. Its attachment architecture is sound, but its member count, runtime, estimand, and floor transport remain intentionally unfrozen.+ impl/d117-u1-ledger-session
+ impl/d117-u3-pinset-v2
  remotes/origin/impl/d117-u1-ledger-session
  remotes/origin/impl/d117-u3-pinset-v2
f665dd4d8bfb7eaca3256a0709b3310254e308fe refs/heads/impl/d117-u1-ledger-session
f665dd4d8bfb7eaca3256a0709b3310254e308fe refs/remotes/origin/impl/d117-u1-ledger-session
origin	https://github.com/mpmdw/JouleWise (fetch)
origin	https://github.com/mpmdw/JouleWise (push)

exec
/bin/zsh -lc 'git ls-remote origin refs/heads/impl/d117-u1-ledger-session' in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 exited 128 in 0ms:
fatal: unable to access 'https://github.com/mpmdw/JouleWise/': Could not resolve host: github.com

codex
Network resolution prevents a fresh origin fetch, and fetching would also violate the explicit no-write constraint. The local branch and its `origin/…` tracking ref are identical at `f665dd4`, so I’m using that exact landed snapshot and will call this limitation out in the plan’s assumptions/open questions.
exec
/bin/zsh -lc 'git log --oneline --decorate --no-merges main..impl/d117-u1-ledger-session; git diff --stat main...impl/d117-u1-ledger-session; git diff --name-status main...impl/d117-u1-ledger-session; git merge-base main impl/d117-u1-ledger-session' in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
c645bd7 U1: two-slot ledger bracket-session capability + exact binding + writer integration, through fix round 1 (L5 mandatory window/runs_root binding; D-109 universe preservation; mid-window pin refusal; exclusive slot claim; candidate-leak closure; WAL torn-tail recovery; discriminating crash/rollback tests; CLI dry-run parity)
 joulewise/calibration_bracketing.py           |  372 +++++++-
 joulewise/calibration_ledger.py               | 1274 ++++++++++++++++++++++++-
 scripts/reserve_calibration_window_bracket.py |  141 +++
 scripts/validate_powermetrics_fiducial.py     |  359 +++++--
 tests/test_calibration_bracketing.py          |  363 +++++++
 tests/test_calibration_ledger.py              |  583 ++++++++++-
 tests/test_powermetrics_fiducial.py           |  256 +++++
 7 files changed, 3240 insertions(+), 108 deletions(-)
M	joulewise/calibration_bracketing.py
M	joulewise/calibration_ledger.py
A	scripts/reserve_calibration_window_bracket.py
M	scripts/validate_powermetrics_fiducial.py
M	tests/test_calibration_bracketing.py
M	tests/test_calibration_ledger.py
M	tests/test_powermetrics_fiducial.py
4628fa0fc0773fca7373566f24b67cb41fa1eb25

2026-08-07T19:19:38.434078Z ERROR codex_models_manager::manager: failed to renew cache TTL: missing field `base_instructions` at line 94 column 5
exec
/bin/zsh -lc "git log --oneline --decorate --max-count=6 impl/d117-u1-ledger-session; git grep -nE '"'^(class|def) |calibration_window_bracket_session|calibration_bracket_binding|bracket_session|finalize.*slot|abort.*slot|discover.*candidate|candidate'"' impl/d117-u1-ledger-session -- joulewise/calibration_ledger.py joulewise/calibration_bracketing.py scripts/reserve_calibration_window_bracket.py tests/test_calibration_ledger.py tests/test_calibration_bracketing.py | head -n 500" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
f665dd4 (origin/impl/d117-u1-ledger-session, impl/d117-u1-ledger-session) Merge main (D-117 index fix) into U1 branch
c645bd7 U1: two-slot ledger bracket-session capability + exact binding + writer integration, through fix round 1 (L5 mandatory window/runs_root binding; D-109 universe preservation; mid-window pin refusal; exclusive slot claim; candidate-leak closure; WAL torn-tail recovery; discriminating crash/rollback tests; CLI dry-run parity)
4628fa0 U1 paired audits custodied (3 BLOCKERs: L5 binding optional, D-109 universe deletion, torn-tail ledger; 2 HIGH live-proofs) + lead FIX contract
4185665 U-unit gauntlet records: U3 paired audits (CRITICAL self-attested-pins live-proof; derived-literal violation) + lead FIX contract; U1/U1b implementation contracts
cf8f26b RUN_STATE live-block refresh: PR #110 merged (paper complete), D-117 + plan-freeze ratified, portfolio adjudicated, U1b/U3-audits in flight, Ed's rulings 1-7 queued
030e17d Three-night operator packet (pre-freeze edition): Sol-drafted per-night checklists + magistrate header with ratified budgets, plan-id scheme, hard pre-night gates, and abort rules
impl/d117-u1-ledger-session:joulewise/calibration_bracketing.py:42:BRACKET_BINDING_SCHEMA = "joulewise.calibration_bracket_binding.v1"
impl/d117-u1-ledger-session:joulewise/calibration_bracketing.py:77:class CalibrationCandidate:
impl/d117-u1-ledger-session:joulewise/calibration_bracketing.py:91:    bracket_session_id: str | None = None
impl/d117-u1-ledger-session:joulewise/calibration_bracketing.py:100:        bound = _candidate_decimal(self)
impl/d117-u1-ledger-session:joulewise/calibration_bracketing.py:114:            "bracket_session_id": self.bracket_session_id,
impl/d117-u1-ledger-session:joulewise/calibration_bracketing.py:124:def _canonical_sha256(value: Mapping[str, Any]) -> str:
impl/d117-u1-ledger-session:joulewise/calibration_bracketing.py:135:def _decimal(value: Any) -> Decimal | None:
impl/d117-u1-ledger-session:joulewise/calibration_bracketing.py:145:def _candidate_decimal(candidate: CalibrationCandidate) -> Decimal | None:
impl/d117-u1-ledger-session:joulewise/calibration_bracketing.py:146:    value = candidate.b_fiducial_s
impl/d117-u1-ledger-session:joulewise/calibration_bracketing.py:159:        # candidates carry strings from authenticated evidence bytes instead.
impl/d117-u1-ledger-session:joulewise/calibration_bracketing.py:166:def _current_estimator_code_sha256() -> dict[str, str] | None:
impl/d117-u1-ledger-session:joulewise/calibration_bracketing.py:176:def _valid_acceptance_bound(value: Any) -> bool:
impl/d117-u1-ledger-session:joulewise/calibration_bracketing.py:188:    backfill = value.get("backfill_candidate")
impl/d117-u1-ledger-session:joulewise/calibration_bracketing.py:203:            and backfill.get("status") == "unratified_candidate_only"
impl/d117-u1-ledger-session:joulewise/calibration_bracketing.py:349:            or backfill.get("candidate_inventory") != disposition_counts
impl/d117-u1-ledger-session:joulewise/calibration_bracketing.py:446:def load_calibration_acceptance_bound(
impl/d117-u1-ledger-session:joulewise/calibration_bracketing.py:458:def _acceptance_bound_from_authenticated_bytes(
impl/d117-u1-ledger-session:joulewise/calibration_bracketing.py:482:def _authenticated_explicit_acceptance_bound(
impl/d117-u1-ledger-session:joulewise/calibration_bracketing.py:493:def _acceptance_artifact_sha256(artifact: Mapping[str, Any]) -> str:
impl/d117-u1-ledger-session:joulewise/calibration_bracketing.py:503:def _valid_sha256(value: Any) -> bool:
impl/d117-u1-ledger-session:joulewise/calibration_bracketing.py:532:def _binding_core(binding: Mapping[str, Any]) -> dict[str, Any]:
impl/d117-u1-ledger-session:joulewise/calibration_bracketing.py:536:def build_calibration_bracket_binding(
impl/d117-u1-ledger-session:joulewise/calibration_bracketing.py:550:    session = ledger_snapshot.bracket_session_by_id.get(session_id)
impl/d117-u1-ledger-session:joulewise/calibration_bracketing.py:571:    pre = session.finalized_slots.get("pre")
impl/d117-u1-ledger-session:joulewise/calibration_bracketing.py:572:    post = session.finalized_slots.get("post")
impl/d117-u1-ledger-session:joulewise/calibration_bracketing.py:612:def validate_calibration_bracket_binding(
impl/d117-u1-ledger-session:joulewise/calibration_bracketing.py:652:    session = ledger_snapshot.bracket_session_by_id.get(str(binding.get("session_id")))
impl/d117-u1-ledger-session:joulewise/calibration_bracketing.py:681:        observation = session.finalized_slots.get(role)
impl/d117-u1-ledger-session:joulewise/calibration_bracketing.py:706:def _binding_evidence_authentic(
impl/d117-u1-ledger-session:joulewise/calibration_bracketing.py:723:    # unmatchable as bracket candidates).
impl/d117-u1-ledger-session:joulewise/calibration_bracketing.py:746:def load_calibration_candidate(
impl/d117-u1-ledger-session:joulewise/calibration_bracketing.py:872:def _candidate_from_observation(
impl/d117-u1-ledger-session:joulewise/calibration_bracketing.py:880:    candidate = load_calibration_candidate(
impl/d117-u1-ledger-session:joulewise/calibration_bracketing.py:884:    if candidate is None:
impl/d117-u1-ledger-session:joulewise/calibration_bracketing.py:886:    bound = _candidate_decimal(candidate)
impl/d117-u1-ledger-session:joulewise/calibration_bracketing.py:893:        candidate.manifest_sha256
impl/d117-u1-ledger-session:joulewise/calibration_bracketing.py:895:        or candidate.evidence_sha256
impl/d117-u1-ledger-session:joulewise/calibration_bracketing.py:902:        or candidate.capture_wall_time_s != receipt_capture
impl/d117-u1-ledger-session:joulewise/calibration_bracketing.py:904:            candidate.bindings.get(field) != observation.t1_bindings.get(field)
impl/d117-u1-ledger-session:joulewise/calibration_bracketing.py:908:            candidate.bindings.get(field) != observation.identity_epoch.get(field)
impl/d117-u1-ledger-session:joulewise/calibration_bracketing.py:914:        candidate,
impl/d117-u1-ledger-session:joulewise/calibration_bracketing.py:919:        bracket_session_id=observation.bracket_session_id,
impl/d117-u1-ledger-session:joulewise/calibration_bracketing.py:929:def discover_calibration_candidates(
impl/d117-u1-ledger-session:joulewise/calibration_bracketing.py:947:        for session in ledger_snapshot.bracket_sessions
impl/d117-u1-ledger-session:joulewise/calibration_bracketing.py:950:    candidates: list[CalibrationCandidate] = []
impl/d117-u1-ledger-session:joulewise/calibration_bracketing.py:955:            or observation.bracket_session_id is not None
impl/d117-u1-ledger-session:joulewise/calibration_bracketing.py:956:            and observation.bracket_session_id not in finalized_session_ids
impl/d117-u1-ledger-session:joulewise/calibration_bracketing.py:959:        candidate = _candidate_from_observation(observation)
impl/d117-u1-ledger-session:joulewise/calibration_bracketing.py:960:        if candidate is None:
impl/d117-u1-ledger-session:joulewise/calibration_bracketing.py:962:        candidates.append(candidate)
impl/d117-u1-ledger-session:joulewise/calibration_bracketing.py:963:    return tuple(candidates)
impl/d117-u1-ledger-session:joulewise/calibration_bracketing.py:966:def _prior_set_matches_import_cutoff_prefix(
impl/d117-u1-ledger-session:joulewise/calibration_bracketing.py:1015:def evaluate_calibration_bracket(
impl/d117-u1-ledger-session:joulewise/calibration_bracketing.py:1016:    candidates: Sequence[CalibrationCandidate],
impl/d117-u1-ledger-session:joulewise/calibration_bracketing.py:1185:            "candidate_set_boundary": (
impl/d117-u1-ledger-session:joulewise/calibration_bracketing.py:1212:        for session in ledger_snapshot.bracket_sessions
impl/d117-u1-ledger-session:joulewise/calibration_bracketing.py:1225:            observation.bracket_session_id is None
impl/d117-u1-ledger-session:joulewise/calibration_bracketing.py:1226:            or observation.bracket_session_id in finalized_session_ids
impl/d117-u1-ledger-session:joulewise/calibration_bracketing.py:1231:            candidate.attempt_id,
impl/d117-u1-ledger-session:joulewise/calibration_bracketing.py:1232:            candidate.content_id,
impl/d117-u1-ledger-session:joulewise/calibration_bracketing.py:1233:            candidate.ledger_receipt_digest,
impl/d117-u1-ledger-session:joulewise/calibration_bracketing.py:1235:        for candidate in candidates
impl/d117-u1-ledger-session:joulewise/calibration_bracketing.py:1239:    # favorable subset while still passing per-candidate membership checks.
impl/d117-u1-ledger-session:joulewise/calibration_bracketing.py:1240:    if supplied_valid != registered_valid or len(candidates) != len(supplied_valid):
impl/d117-u1-ledger-session:joulewise/calibration_bracketing.py:1242:    for candidate in candidates:
impl/d117-u1-ledger-session:joulewise/calibration_bracketing.py:1244:            observations_by_attempt.get(candidate.attempt_id)
impl/d117-u1-ledger-session:joulewise/calibration_bracketing.py:1245:            if isinstance(candidate.attempt_id, str)
impl/d117-u1-ledger-session:joulewise/calibration_bracketing.py:1251:            or candidate.content_id != observation.content_id
impl/d117-u1-ledger-session:joulewise/calibration_bracketing.py:1252:            or candidate.ledger_receipt_digest != observation.receipt_digest
impl/d117-u1-ledger-session:joulewise/calibration_bracketing.py:1253:            or candidate.manifest_sha256
impl/d117-u1-ledger-session:joulewise/calibration_bracketing.py:1255:            or candidate.evidence_sha256
impl/d117-u1-ledger-session:joulewise/calibration_bracketing.py:1257:            or candidate.bracket_session_id != observation.bracket_session_id
impl/d117-u1-ledger-session:joulewise/calibration_bracketing.py:1258:            or candidate.bracket_slot != observation.bracket_slot
impl/d117-u1-ledger-session:joulewise/calibration_bracketing.py:1259:            or candidate.bracket_window_id != observation.bracket_window_id
impl/d117-u1-ledger-session:joulewise/calibration_bracketing.py:1260:            or candidate.bracket_plan_id != observation.bracket_plan_id
impl/d117-u1-ledger-session:joulewise/calibration_bracketing.py:1261:            or candidate.bracket_plan_sha256
impl/d117-u1-ledger-session:joulewise/calibration_bracketing.py:1263:            or candidate.bracket_evidence_root_id
impl/d117-u1-ledger-session:joulewise/calibration_bracketing.py:1265:            or candidate.bracket_runs_root != observation.bracket_runs_root
impl/d117-u1-ledger-session:joulewise/calibration_bracketing.py:1268:    has_session_candidates = any(
impl/d117-u1-ledger-session:joulewise/calibration_bracketing.py:1269:        candidate.bracket_session_id is not None for candidate in candidates
impl/d117-u1-ledger-session:joulewise/calibration_bracketing.py:1272:    if has_session_candidates:
impl/d117-u1-ledger-session:joulewise/calibration_bracketing.py:1286:            return result, ("calibration_bracket_binding_missing",)
impl/d117-u1-ledger-session:joulewise/calibration_bracketing.py:1288:        bound_observations = validate_calibration_bracket_binding(
impl/d117-u1-ledger-session:joulewise/calibration_bracketing.py:1298:            return result, ("calibration_bracket_binding_invalid",)
impl/d117-u1-ledger-session:joulewise/calibration_bracketing.py:1310:        for candidate in candidates:
impl/d117-u1-ledger-session:joulewise/calibration_bracketing.py:1311:            if candidate.bracket_session_id != bound_session_id:
impl/d117-u1-ledger-session:joulewise/calibration_bracketing.py:1314:                candidate.bracket_window_id,
impl/d117-u1-ledger-session:joulewise/calibration_bracketing.py:1315:                candidate.bracket_plan_id,
impl/d117-u1-ledger-session:joulewise/calibration_bracketing.py:1316:                candidate.bracket_plan_sha256,
impl/d117-u1-ledger-session:joulewise/calibration_bracketing.py:1317:                candidate.bracket_evidence_root_id,
impl/d117-u1-ledger-session:joulewise/calibration_bracketing.py:1318:                candidate.bracket_runs_root,
impl/d117-u1-ledger-session:joulewise/calibration_bracketing.py:1326:                return result, ("calibration_bracket_binding_invalid",)
impl/d117-u1-ledger-session:joulewise/calibration_bracketing.py:1330:        candidate
impl/d117-u1-ledger-session:joulewise/calibration_bracketing.py:1331:        for candidate in candidates
impl/d117-u1-ledger-session:joulewise/calibration_bracketing.py:1332:        if candidate.protocol_id == PROTOCOL_ID
impl/d117-u1-ledger-session:joulewise/calibration_bracketing.py:1334:            candidate.bindings.get(field) == bindings.get(field)
impl/d117-u1-ledger-session:joulewise/calibration_bracketing.py:1339:    for candidate in matching:
impl/d117-u1-ledger-session:joulewise/calibration_bracketing.py:1340:        candidate_decimal = _candidate_decimal(candidate)
impl/d117-u1-ledger-session:joulewise/calibration_bracketing.py:1341:        if candidate_decimal is None or candidate_decimal < 0:
impl/d117-u1-ledger-session:joulewise/calibration_bracketing.py:1343:        matching_decimals[id(candidate)] = candidate_decimal
impl/d117-u1-ledger-session:joulewise/calibration_bracketing.py:1422:    # narrower bracket-candidate set.  A governed aborted PRE can therefore
impl/d117-u1-ledger-session:joulewise/calibration_bracketing.py:1440:        candidate for candidate in matching if candidate.capture_wall_time_s <= window_start_s
impl/d117-u1-ledger-session:joulewise/calibration_bracketing.py:1443:        candidate for candidate in matching if candidate.capture_wall_time_s >= window_end_s
impl/d117-u1-ledger-session:joulewise/calibration_bracketing.py:1446:        candidate
impl/d117-u1-ledger-session:joulewise/calibration_bracketing.py:1447:        for candidate in causal_pre
impl/d117-u1-ledger-session:joulewise/calibration_bracketing.py:1448:        if window_end_s <= candidate.capture_wall_time_s + MAX_AGE_S
impl/d117-u1-ledger-session:joulewise/calibration_bracketing.py:1451:        candidate
impl/d117-u1-ledger-session:joulewise/calibration_bracketing.py:1452:        for candidate in causal_post
impl/d117-u1-ledger-session:joulewise/calibration_bracketing.py:1453:        if candidate.capture_wall_time_s - window_start_s <= MAX_AGE_S
impl/d117-u1-ledger-session:joulewise/calibration_bracketing.py:1463:        pre = max(fresh_pre, key=lambda candidate: candidate.capture_wall_time_s)
impl/d117-u1-ledger-session:joulewise/calibration_bracketing.py:1464:        post = min(fresh_post, key=lambda candidate: candidate.capture_wall_time_s)
impl/d117-u1-ledger-session:joulewise/calibration_bracketing.py:1466:        candidate_by_receipt = {
impl/d117-u1-ledger-session:joulewise/calibration_bracketing.py:1467:            candidate.ledger_receipt_digest: candidate for candidate in matching
impl/d117-u1-ledger-session:joulewise/calibration_bracketing.py:1469:        pre = candidate_by_receipt.get(bound_observations[0].receipt_digest)
impl/d117-u1-ledger-session:joulewise/calibration_bracketing.py:1470:        post = candidate_by_receipt.get(bound_observations[1].receipt_digest)
impl/d117-u1-ledger-session:joulewise/calibration_bracketing.py:1472:            return result, ("calibration_bracket_binding_invalid",)
impl/d117-u1-ledger-session:joulewise/calibration_bracketing.py:1487:        # authenticated production candidates always use the exact branch.
impl/d117-u1-ledger-session:joulewise/calibration_bracketing.py:1598:def calibration_bracket_for_bundles(
impl/d117-u1-ledger-session:joulewise/calibration_bracketing.py:1664:        candidates: tuple[CalibrationCandidate, ...] = ()
impl/d117-u1-ledger-session:joulewise/calibration_bracketing.py:1666:        candidates = discover_calibration_candidates(ledger_snapshot)
impl/d117-u1-ledger-session:joulewise/calibration_bracketing.py:1671:                observation.bracket_session_id is None
impl/d117-u1-ledger-session:joulewise/calibration_bracketing.py:1673:                    session.session_id == observation.bracket_session_id
impl/d117-u1-ledger-session:joulewise/calibration_bracketing.py:1675:                    for session in ledger_snapshot.bracket_sessions
impl/d117-u1-ledger-session:joulewise/calibration_bracketing.py:1680:        if ledger_snapshot.valid and len(candidates) != registered_valid:
impl/d117-u1-ledger-session:joulewise/calibration_bracketing.py:1692:        candidates,
impl/d117-u1-ledger-session:joulewise/calibration_bracketing.py:1714:    "build_calibration_bracket_binding",
impl/d117-u1-ledger-session:joulewise/calibration_bracketing.py:1716:    "discover_calibration_candidates",
impl/d117-u1-ledger-session:joulewise/calibration_bracketing.py:1719:    "load_calibration_candidate",
impl/d117-u1-ledger-session:joulewise/calibration_bracketing.py:1720:    "validate_calibration_bracket_binding",
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:46:BRACKET_SESSION_SCHEMA = "joulewise.calibration_window_bracket_session.v1"
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:119:        "calibration_ledger_bracket_session_conflict": "a bracket session has duplicate, reordered, or conflicting state transitions",
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:121:        "calibration_ledger_bracket_session_open": "a bracket session has not finalized both slots or recorded a governed abort",
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:137:class CalibrationLedgerError(ValueError):
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:141:def _jsonable(value: Any) -> Any:
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:149:def canonical_json_bytes(value: Mapping[str, Any]) -> bytes:
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:159:def canonical_sha256(value: Mapping[str, Any]) -> str:
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:163:def _is_sha256(value: object) -> bool:
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:167:def _normalized_vector(
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:175:def content_id_from_artifact_hashes(artifact_sha256: Mapping[str, Any]) -> str | None:
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:192:def artifact_hashes(custody_dir: Path) -> dict[str, str]:
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:204:def receipt_core(receipt: Mapping[str, Any]) -> dict[str, Any]:
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:208:def _receipt_digest(receipt: Mapping[str, Any]) -> str:
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:213:class LedgerObservation:
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:226:    bracket_session_id: str | None = None
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:248:class CalibrationLedgerSnapshot:
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:258:    bracket_sessions: tuple["CalibrationBracketSession", ...] = ()
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:275:    def bracket_session_by_id(self) -> Mapping[str, "CalibrationBracketSession"]:
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:277:            {session.session_id: session for session in self.bracket_sessions}
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:285:            "calibration_ledger_bracket_session_open",
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:295:            session for session in self.bracket_sessions if session.state == "open"
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:344:class CalibrationBracketSession:
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:357:    finalized_slots: Mapping[str, LedgerObservation]
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:363:class HistoricalImportPlan:
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:378:class HistoricalImportDurabilityUncertain(CalibrationLedgerError):
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:391:class _HistoricalCandidate:
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:403:def _frozen_mapping(value: Mapping[str, Any]) -> Mapping[str, Any]:
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:487:    | {"finalized_slots", "unused_slots", "reason"}
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:500:def _valid_chain_fields(receipt: Mapping[str, Any], schema: str) -> bool:
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:514:def _valid_session_identity(receipt: Mapping[str, Any]) -> bool:
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:530:def _valid_session_slot_reservation(slot: object, expected_role: str) -> bool:
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:550:def _valid_session_receipt_shape(receipt: Mapping[str, Any]) -> bool:
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:585:        finalized = receipt.get("finalized_slots")
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:638:def _valid_receipt_shape(receipt: object) -> bool:
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:740:def _head_pin(value: object) -> tuple[int, str] | None:
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:761:def _committed_pin_bytes(path: Path, repo_root: Path) -> bytes | None:
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:779:def _append_journal_path(ledger_path: Path) -> Path:
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:784:def _append_recovery_path(ledger_path: Path, operation_id: str) -> Path:
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:789:def _journal_core(value: Mapping[str, Any]) -> dict[str, Any]:
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:793:def _valid_append_journal(value: object) -> bool:
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:826:def _read_append_journal(ledger_path: Path) -> tuple[Mapping[str, Any] | None, bool]:
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:843:def _journal_completed_raw(
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:869:def _parse_ledger(
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:918:def _observation_from_receipt(
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:938:        bracket_session_id=(str(session["session_id"]) if session else None),
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:950:def _session_identity_matches(
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:956:def _bracket_sessions_and_observations(
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:971:                reasons.add("calibration_ledger_bracket_session_conflict")
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:983:            reasons.add("calibration_ledger_bracket_session_conflict")
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:987:            reasons.add("calibration_ledger_bracket_session_conflict")
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:1005:                reasons.add("calibration_ledger_bracket_session_conflict")
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:1023:                reasons.add("calibration_ledger_bracket_session_conflict")
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:1027:        finalized_slots = list(finals)
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:1033:            or receipt["finalized_slots"] != finalized_slots
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:1036:            reasons.add("calibration_ledger_bracket_session_conflict")
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:1054:            reasons.add("calibration_ledger_bracket_session_open")
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:1070:        # is governed-terminal; candidate discovery applies the narrower
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:1074:                finalized_observations[slot]
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:1095:                finalized_slots=MappingProxyType(finalized_observations),
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:1105:def _attempts_and_observations(
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:1173:        _bracket_sessions_and_observations(receipts)
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:1182:        reasons.add("calibration_ledger_bracket_session_conflict")
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:1190:        for observation in session.finalized_slots.values()
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:1211:def _custody_reasons(
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:1233:def load_calibration_ledger_snapshot(
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:1326:    observations, bracket_sessions, state_reasons = _attempts_and_observations(
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:1333:        for session in bracket_sessions:
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:1336:                for observation in session.finalized_slots.values()
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:1348:        bracket_sessions=tuple(bracket_sessions),
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:1356:def _new_receipt(
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:1396:def _new_bracket_session_record(
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:1417:def _json_object_from_bytes(raw: bytes, source: Path) -> Mapping[str, Any]:
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:1427:def _authenticated_json_object(
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:1441:def _number_lexemes(raw: bytes, source: Path) -> Mapping[str, Any]:
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:1451:def _historical_import_table(
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:1514:def _historical_import_custody_manifest(
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:1543:def custody_manifest_bytes(value: Mapping[str, Any]) -> bytes:
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:1558:def _historical_directories(roots: Sequence[Path]) -> tuple[Path, ...]:
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:1577:        raise CalibrationLedgerError("historical import roots contain no candidates")
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:1581:def _assert_absolute_nonsymlink_directory(directory: Path) -> Path:
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:1602:def _read_contained_nofollow(directory: Path, relative: str) -> bytes:
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:1649:def _governed_raw_nofollow(directory: Path) -> dict[str, bytes]:
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:1656:def _inspect_historical_candidate(
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:1768:def _discover_historical_candidates(
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:1783:        content_id, candidate, error = _inspect_historical_candidate(
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:1788:        if candidate is not None:
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:1789:            complete.setdefault(candidate.content_id, []).append(candidate)
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:1801:def generate_historical_custody_manifest(
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:1816:    complete, incomplete = _discover_historical_candidates(
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:1837:        candidate = min(
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:1841:        if candidate.attempt_id != member["attempt_id"]:
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:1845:        if dict(candidate.artifact_sha256) != dict(member["artifact_sha256"]):
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:1849:        members[content_id] = candidate.custody_locator
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:1857:def prepare_historical_import(
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:1886:        observed_id, candidate, error = _inspect_historical_candidate(
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:1891:        if candidate is None:
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:1899:        selected_by_content[content_id] = candidate
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:1902:        complete, _incomplete = _discover_historical_candidates(
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:1913:            candidate.custody_locator
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:1914:            for candidates in complete.values()
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:1915:            for candidate in candidates
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:1929:        candidate = selected_by_content[content_id]
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:1930:        if candidate.attempt_id != member["attempt_id"]:
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:1934:        if dict(candidate.artifact_sha256) != dict(member["artifact_sha256"]):
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:1938:        selected.append((candidate, member))
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:1945:    for candidate, member in selected:
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:1950:            attempt_id=candidate.attempt_id,
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:1953:            identity_epoch=candidate.identity_epoch,
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:1954:            t1_bindings=candidate.t1_bindings,
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:1958:            custody_locator=candidate.custody_locator,
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:1972:            attempt_id=candidate.attempt_id,
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:1973:            content_id=candidate.content_id,
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:1974:            artifacts=candidate.artifact_sha256,
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:1975:            identity_epoch=candidate.identity_epoch,
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:1976:            t1_bindings=candidate.t1_bindings,
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:1977:            capture_wall_time_s=candidate.capture_wall_time_s,
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:1978:            exact_bound_lexeme_s=candidate.exact_bound_lexeme_s,
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:1980:            custody_locator=candidate.custody_locator,
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:1987:    observations, bracket_sessions, reasons = _attempts_and_observations(receipts)
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:1988:    del bracket_sessions
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:2005:def _require_genesis_bootstrap_state(
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:2040:def _ledger_lock_path(ledger_path: Path) -> Path:
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:2045:def _open_ledger_lock(ledger_path: Path) -> int:
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:2085:def _fsync_parent_directory(path: Path) -> None:
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:2110:def _write_bootstrap_payload(handle: BinaryIO, payload: bytes) -> None:
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:2116:def _reauthenticate_historical_import_plan(plan: HistoricalImportPlan) -> None:
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:2136:def bootstrap_historical_import(
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:2242:def _atomic_private_write(path: Path, payload: bytes) -> None:
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:2271:def _prepare_append_journal(
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:2294:def _write_ledger_append_payload(handle: BinaryIO, payload: bytes) -> None:
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:2302:def _record_append_recovery(
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:2334:def _clear_append_journal(ledger_path: Path) -> None:
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:2342:def _recover_journaled_append(
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:2376:def _locked_append(
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:2430:def _authenticated_head_pin(
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:2450:def validate_bracket_session_reservation_inputs(
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:2509:def append_bracket_session_receipt(
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:2531:    session_identity, normalized_slots = validate_bracket_session_reservation_inputs(
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:2574:        return _new_bracket_session_record(
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:2585:def claim_bracket_session_slot(
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:2603:        non_open_reasons = reasons - {"calibration_ledger_bracket_session_open"}
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:2611:        expected_slot = BRACKET_SESSION_SLOTS[len(session.finalized_slots)]
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:2633:        return _new_bracket_session_record(
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:2650:def finalize_bracket_session_slot(
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:2677:        non_open_reasons = reasons - {"calibration_ledger_bracket_session_open"}
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:2684:        expected_slot = BRACKET_SESSION_SLOTS[len(session.finalized_slots)]
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:2685:        if slot != expected_slot or slot in session.finalized_slots:
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:2687:                f"bracket session slot must finalize in order: expected {expected_slot}"
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:2705:        return _new_bracket_session_record(
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:2729:def abort_bracket_session(
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:2743:        non_open_reasons = reasons - {"calibration_ledger_bracket_session_open"}
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:2758:        finalized_slots = list(session.finalized_slots)
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:2759:        return _new_bracket_session_record(
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:2767:                "finalized_slots": finalized_slots,
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:2769:                    role for role in BRACKET_SESSION_SLOTS if role not in finalized_slots
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:2778:def terminal_head_pin_for_session(
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:2783:    """Return the sole terminal pin candidate after post or governed abort."""
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:2799:        session.finalized_slots["post"].receipt_digest
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:2809:def append_pending_receipt(
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:2848:        observations, bracket_sessions, reasons = _attempts_and_observations(receipts)
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:2850:        del bracket_sessions
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:2884:def finalize_attempt_receipt(
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:2904:        observations, bracket_sessions, reasons = _attempts_and_observations(
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:2907:        del observations, bracket_sessions
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:2955:def _head_pin_for_valid_receipt(receipt: Mapping[str, Any]) -> dict[str, Any]:
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:2965:def head_pin_for_receipt(receipt: Mapping[str, Any]) -> dict[str, Any]:
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:3005:    "append_bracket_session_receipt",
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:3006:    "claim_bracket_session_slot",
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:3007:    "abort_bracket_session",
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:3014:    "finalize_bracket_session_slot",
impl/d117-u1-ledger-session:joulewise/calibration_ledger.py:3020:    "validate_bracket_session_reservation_inputs",
impl/d117-u1-ledger-session:scripts/reserve_calibration_window_bracket.py:26:    append_bracket_session_receipt,
impl/d117-u1-ledger-session:scripts/reserve_calibration_window_bracket.py:28:    validate_bracket_session_reservation_inputs,
impl/d117-u1-ledger-session:scripts/reserve_calibration_window_bracket.py:35:def _json_object(path: Path) -> Mapping[str, Any]:
impl/d117-u1-ledger-session:scripts/reserve_calibration_window_bracket.py:42:def _parser() -> argparse.ArgumentParser:
impl/d117-u1-ledger-session:scripts/reserve_calibration_window_bracket.py:71:def main(argv: list[str] | None = None) -> int:
impl/d117-u1-ledger-session:scripts/reserve_calibration_window_bracket.py:91:            validate_bracket_session_reservation_inputs(
impl/d117-u1-ledger-session:scripts/reserve_calibration_window_bracket.py:113:            receipt = append_bracket_session_receipt(
impl/d117-u1-ledger-session:tests/test_calibration_bracketing.py:26:    build_calibration_bracket_binding,
impl/d117-u1-ledger-session:tests/test_calibration_bracketing.py:28:    discover_calibration_candidates,
impl/d117-u1-ledger-session:tests/test_calibration_bracketing.py:31:    load_calibration_candidate,
impl/d117-u1-ledger-session:tests/test_calibration_bracketing.py:32:    validate_calibration_bracket_binding,
impl/d117-u1-ledger-session:tests/test_calibration_bracketing.py:161:def _unissued_acceptance_fixture_bytes() -> bytes:
impl/d117-u1-ledger-session:tests/test_calibration_bracketing.py:170:def _unissued_acceptance_fixture() -> dict:
impl/d117-u1-ledger-session:tests/test_calibration_bracketing.py:176:def _synthetic_issued_artifact() -> dict:
impl/d117-u1-ledger-session:tests/test_calibration_bracketing.py:220:    artifact["backfill_candidate"].update(
impl/d117-u1-ledger-session:tests/test_calibration_bracketing.py:223:            "candidate_inventory": {
impl/d117-u1-ledger-session:tests/test_calibration_bracketing.py:243:def _synthetic_issued_snapshot(
impl/d117-u1-ledger-session:tests/test_calibration_bracketing.py:282:def _fixture_snapshot(
impl/d117-u1-ledger-session:tests/test_calibration_bracketing.py:283:    candidates: list[CalibrationCandidate],
impl/d117-u1-ledger-session:tests/test_calibration_bracketing.py:291:    for index, candidate in enumerate(candidates):
impl/d117-u1-ledger-session:tests/test_calibration_bracketing.py:292:        attempt_id = candidate.attempt_id or f"fixture-attempt-{index}-{candidate.relative_path}"
impl/d117-u1-ledger-session:tests/test_calibration_bracketing.py:294:            "manifest.json": candidate.manifest_sha256,
impl/d117-u1-ledger-session:tests/test_calibration_bracketing.py:295:            "instrument_evidence.json": candidate.evidence_sha256,
impl/d117-u1-ledger-session:tests/test_calibration_bracketing.py:297:        content_id = candidate.content_id or content_id_from_artifact_hashes(hashes)
impl/d117-u1-ledger-session:tests/test_calibration_bracketing.py:299:        digest = candidate.ledger_receipt_digest or hashlib.sha256(
impl/d117-u1-ledger-session:tests/test_calibration_bracketing.py:302:        bound = str(candidate.b_fiducial_s)
impl/d117-u1-ledger-session:tests/test_calibration_bracketing.py:303:        normalized_candidate = replace(
impl/d117-u1-ledger-session:tests/test_calibration_bracketing.py:304:            candidate,
impl/d117-u1-ledger-session:tests/test_calibration_bracketing.py:309:        normalized.append(normalized_candidate)
impl/d117-u1-ledger-session:tests/test_calibration_bracketing.py:319:                        field: candidate.bindings.get(field)
impl/d117-u1-ledger-session:tests/test_calibration_bracketing.py:331:                    {field: candidate.bindings.get(field) for field in V2_BINDING_FIELDS}
impl/d117-u1-ledger-session:tests/test_calibration_bracketing.py:333:                capture_wall_time_s=str(candidate.capture_wall_time_s),
impl/d117-u1-ledger-session:tests/test_calibration_bracketing.py:336:                custody_locator=candidate.relative_path,
impl/d117-u1-ledger-session:tests/test_calibration_bracketing.py:360:def _evaluate_with_unissued_acceptance(
impl/d117-u1-ledger-session:tests/test_calibration_bracketing.py:361:    candidates: list[CalibrationCandidate] | tuple[CalibrationCandidate, ...],
impl/d117-u1-ledger-session:tests/test_calibration_bracketing.py:370:        return _evaluate_calibration_bracket(candidates, **kwargs)
impl/d117-u1-ledger-session:tests/test_calibration_bracketing.py:373:def evaluate_calibration_bracket(
impl/d117-u1-ledger-session:tests/test_calibration_bracketing.py:374:    candidates: list[CalibrationCandidate], **kwargs: object
impl/d117-u1-ledger-session:tests/test_calibration_bracketing.py:376:    snapshot, normalized = _fixture_snapshot(list(candidates))
impl/d117-u1-ledger-session:tests/test_calibration_bracketing.py:385:class CalibrationBracketingTests(unittest.TestCase):
impl/d117-u1-ledger-session:tests/test_calibration_bracketing.py:405:        snapshot, candidates = _fixture_snapshot(
impl/d117-u1-ledger-session:tests/test_calibration_bracketing.py:407:                self.candidate("pre", 99.0, "0.025"),
impl/d117-u1-ledger-session:tests/test_calibration_bracketing.py:408:                self.candidate("post", 111.0, "0.026"),
impl/d117-u1-ledger-session:tests/test_calibration_bracketing.py:416:                candidates,
impl/d117-u1-ledger-session:tests/test_calibration_bracketing.py:720:        candidates = [
impl/d117-u1-ledger-session:tests/test_calibration_bracketing.py:721:            self.candidate("pre", 99.0, "0.025"),
impl/d117-u1-ledger-session:tests/test_calibration_bracketing.py:722:            self.candidate("post", 111.0, "0.026"),
impl/d117-u1-ledger-session:tests/test_calibration_bracketing.py:724:        snapshot, registered = _fixture_snapshot(candidates)
impl/d117-u1-ledger-session:tests/test_calibration_bracketing.py:764:            candidate.attempt_id: candidate for candidate in registered
impl/d117-u1-ledger-session:tests/test_calibration_bracketing.py:767:            "joulewise.calibration_bracketing._candidate_from_observation",
impl/d117-u1-ledger-session:tests/test_calibration_bracketing.py:770:            discovered = discover_calibration_candidates(snapshot)
impl/d117-u1-ledger-session:tests/test_calibration_bracketing.py:796:                self.candidate("pre", 99.0, "0.025"),
impl/d117-u1-ledger-session:tests/test_calibration_bracketing.py:797:                self.candidate("post", 111.0, "0.026"),
impl/d117-u1-ledger-session:tests/test_calibration_bracketing.py:827:    def candidate(
impl/d117-u1-ledger-session:tests/test_calibration_bracketing.py:879:        candidates = []
impl/d117-u1-ledger-session:tests/test_calibration_bracketing.py:890:            candidate = replace(
impl/d117-u1-ledger-session:tests/test_calibration_bracketing.py:891:                self.candidate(name, capture, bound),
impl/d117-u1-ledger-session:tests/test_calibration_bracketing.py:897:                bracket_session_id=session_id,
impl/d117-u1-ledger-session:tests/test_calibration_bracketing.py:905:            candidates.append(candidate)
impl/d117-u1-ledger-session:tests/test_calibration_bracketing.py:934:                    bracket_session_id=session_id,
impl/d117-u1-ledger-session:tests/test_calibration_bracketing.py:964:            finalized_slots=MappingProxyType(by_slot),
impl/d117-u1-ledger-session:tests/test_calibration_bracketing.py:984:            bracket_sessions=(session,),
impl/d117-u1-ledger-session:tests/test_calibration_bracketing.py:988:        binding = build_calibration_bracket_binding(
impl/d117-u1-ledger-session:tests/test_calibration_bracketing.py:997:        return snapshot, candidates, binding
impl/d117-u1-ledger-session:tests/test_calibration_bracketing.py:1000:        snapshot, candidates, binding = self._bound_session_fixture()
impl/d117-u1-ledger-session:tests/test_calibration_bracketing.py:1001:        resolved = validate_calibration_bracket_binding(
impl/d117-u1-ledger-session:tests/test_calibration_bracketing.py:1016:                candidates,
impl/d117-u1-ledger-session:tests/test_calibration_bracketing.py:1041:        snapshot, candidates, binding = self._bound_session_fixture()
impl/d117-u1-ledger-session:tests/test_calibration_bracketing.py:1043:            candidates[-1],
impl/d117-u1-ledger-session:tests/test_calibration_bracketing.py:1047:        supplied = [*candidates[:-1], later_other_root]
impl/d117-u1-ledger-session:tests/test_calibration_bracketing.py:1074:                candidates,
impl/d117-u1-ledger-session:tests/test_calibration_bracketing.py:1088:        self.assertEqual(reasons, ("calibration_bracket_binding_invalid",))
impl/d117-u1-ledger-session:tests/test_calibration_bracketing.py:1090:    def test_session_candidates_refuse_missing_neighbor_substituted_or_cross_window_binding(
impl/d117-u1-ledger-session:tests/test_calibration_bracketing.py:1093:        snapshot, candidates, binding = self._bound_session_fixture()
impl/d117-u1-ledger-session:tests/test_calibration_bracketing.py:1094:        self.assertIsNone(validate_calibration_bracket_binding(binding, snapshot))
impl/d117-u1-ledger-session:tests/test_calibration_bracketing.py:1100:                candidates,
impl/d117-u1-ledger-session:tests/test_calibration_bracketing.py:1108:        self.assertEqual(reasons, ("calibration_bracket_binding_missing",))
impl/d117-u1-ledger-session:tests/test_calibration_bracketing.py:1112:            "attempt_id": candidates[0].attempt_id,
impl/d117-u1-ledger-session:tests/test_calibration_bracketing.py:1113:            "receipt_digest": candidates[0].ledger_receipt_digest,
impl/d117-u1-ledger-session:tests/test_calibration_bracketing.py:1114:            "content_digest": candidates[0].content_id,
impl/d117-u1-ledger-session:tests/test_calibration_bracketing.py:1124:            validate_calibration_bracket_binding(
impl/d117-u1-ledger-session:tests/test_calibration_bracketing.py:1145:            validate_calibration_bracket_binding(
impl/d117-u1-ledger-session:tests/test_calibration_bracketing.py:1156:    def test_open_and_aborted_session_observations_never_leak_as_candidates(self) -> None:
impl/d117-u1-ledger-session:tests/test_calibration_bracketing.py:1157:        snapshot, candidates, _binding = self._bound_session_fixture()
impl/d117-u1-ledger-session:tests/test_calibration_bracketing.py:1158:        session = snapshot.bracket_sessions[0]
impl/d117-u1-ledger-session:tests/test_calibration_bracketing.py:1162:            finalized_slots=MappingProxyType({"pre": session.finalized_slots["pre"]}),
impl/d117-u1-ledger-session:tests/test_calibration_bracketing.py:1171:            bracket_sessions=(open_session,),
impl/d117-u1-ledger-session:tests/test_calibration_bracketing.py:1173:            head_digest=session.finalized_slots["pre"].receipt_digest,
impl/d117-u1-ledger-session:tests/test_calibration_bracketing.py:1188:                        "receipt_digest": session.finalized_slots["pre"].receipt_digest,
impl/d117-u1-ledger-session:tests/test_calibration_bracketing.py:1193:                "calibration_ledger_bracket_session_open",
impl/d117-u1-ledger-session:tests/test_calibration_bracketing.py:1199:        by_attempt = {candidate.attempt_id: candidate for candidate in candidates}
impl/d117-u1-ledger-session:tests/test_calibration_bracketing.py:1201:            "joulewise.calibration_bracketing._candidate_from_observation",
impl/d117-u1-ledger-session:tests/test_calibration_bracketing.py:1204:            open_candidates = discover_calibration_candidates(open_snapshot)
impl/d117-u1-ledger-session:tests/test_calibration_bracketing.py:1206:            [candidate.bracket_session_id for candidate in open_candidates],
impl/d117-u1-ledger-session:tests/test_calibration_bracketing.py:1218:            bracket_sessions=(aborted_session,),
impl/d117-u1-ledger-session:tests/test_calibration_bracketing.py:1222:            "joulewise.calibration_bracketing._candidate_from_observation",
impl/d117-u1-ledger-session:tests/test_calibration_bracketing.py:1225:            discovered = discover_calibration_candidates(aborted_snapshot)
impl/d117-u1-ledger-session:tests/test_calibration_bracketing.py:1227:            [candidate.bracket_session_id for candidate in discovered],
impl/d117-u1-ledger-session:tests/test_calibration_bracketing.py:1235:            [self.candidate("pre", 99.0, 0.020), self.candidate("post", 111.0, 0.027)],
impl/d117-u1-ledger-session:tests/test_calibration_bracketing.py:1249:            [self.candidate("pre", 99.0, 0.020)],
impl/d117-u1-ledger-session:tests/test_calibration_bracketing.py:1258:    def test_claim_bracket_refuses_v2_only_candidates_but_accepts_v3_pair(self) -> None:
impl/d117-u1-ledger-session:tests/test_calibration_bracketing.py:1263:            self.candidate("pre-v2", 99.0, 0.020, protocol_id=PROTOCOL_V2_ID),
impl/d117-u1-ledger-session:tests/test_calibration_bracketing.py:1264:            self.candidate("post-v2", 111.0, 0.027, protocol_id=PROTOCOL_V2_ID),
impl/d117-u1-ledger-session:tests/test_calibration_bracketing.py:1277:            self.candidate("pre-v3", 99.0, 0.020),
impl/d117-u1-ledger-session:tests/test_calibration_bracketing.py:1278:            self.candidate("post-v3", 111.0, 0.027),
impl/d117-u1-ledger-session:tests/test_calibration_bracketing.py:1292:            [self.candidate("pre", 99.0, 0.020), self.candidate("post", 111.0, 0.035)],
impl/d117-u1-ledger-session:tests/test_calibration_bracketing.py:1304:            [self.candidate("pre", 99.0, 0.020), self.candidate("post", 111.0, 0.031)],
impl/d117-u1-ledger-session:tests/test_calibration_bracketing.py:1324:            [self.candidate("pre", 99.0, 0.020), self.candidate("post", 111.0, 0.035)],
impl/d117-u1-ledger-session:tests/test_calibration_bracketing.py:1356:                        self.candidate("pre", 99.0, "0.020"),
impl/d117-u1-ledger-session:tests/test_calibration_bracketing.py:1357:                        self.candidate("post", 111.0, post),
impl/d117-u1-ledger-session:tests/test_calibration_bracketing.py:1379:                self.candidate("pre", 99.0, 0.020),
impl/d117-u1-ledger-session:tests/test_calibration_bracketing.py:1380:                self.candidate("post", 111.0, one_binary64_ulp_beyond),
impl/d117-u1-ledger-session:tests/test_calibration_bracketing.py:1396:                self.candidate("pre", 99.0, "0.025"),
impl/d117-u1-ledger-session:tests/test_calibration_bracketing.py:1397:                self.candidate("post", 111.0, "0.025"),
impl/d117-u1-ledger-session:tests/test_calibration_bracketing.py:1408:    def test_t1_mismatched_candidate_remains_ineligible_under_d079_v2(self) -> None:
impl/d117-u1-ledger-session:tests/test_calibration_bracketing.py:1413:                self.candidate("pre", 99.0, 0.020),
impl/d117-u1-ledger-session:tests/test_calibration_bracketing.py:1414:                self.candidate("post-mismatch", 111.0, 0.020, bindings=mismatched),
impl/d117-u1-ledger-session:tests/test_calibration_bracketing.py:1434:                self.candidate("window-a-pre", 99.0, 0.022),
impl/d117-u1-ledger-session:tests/test_calibration_bracketing.py:1435:                self.candidate(
impl/d117-u1-ledger-session:tests/test_calibration_bracketing.py:1457:                self.candidate("pre", 99.0, 0.020, bindings=changed_epoch),
impl/d117-u1-ledger-session:tests/test_calibration_bracketing.py:1458:                self.candidate("post", 111.0, 0.021, bindings=changed_epoch),
impl/d117-u1-ledger-session:tests/test_calibration_bracketing.py:1476:                self.candidate("pre", 99.0, "0.025", bindings=changed),
impl/d117-u1-ledger-session:tests/test_calibration_bracketing.py:1477:                self.candidate("post", 111.0, "0.026", bindings=changed),
impl/d117-u1-ledger-session:tests/test_calibration_bracketing.py:1503:            [self.candidate("pre", 99.0, 0.034), self.candidate("post", 111.0, 0.023)],
impl/d117-u1-ledger-session:tests/test_calibration_bracketing.py:1527:                self.candidate(
impl/d117-u1-ledger-session:tests/test_calibration_bracketing.py:1532:                self.candidate("window-b-post", 111.0, "0.023"),
impl/d117-u1-ledger-session:tests/test_calibration_bracketing.py:1556:                    self.candidate("range-expander", 99.0, "0.022"),
impl/d117-u1-ledger-session:tests/test_calibration_bracketing.py:1562:                self.candidate("current-pre", 199.0, "0.025"),
impl/d117-u1-ledger-session:tests/test_calibration_bracketing.py:1563:                self.candidate("current-post", 211.0, "0.026"),
impl/d117-u1-ledger-session:tests/test_calibration_bracketing.py:1582:                "joulewise.calibration_bracketing.discover_calibration_candidates",
impl/d117-u1-ledger-session:tests/test_calibration_bracketing.py:1602:                "candidate_set_boundary"
impl/d117-u1-ledger-session:tests/test_calibration_bracketing.py:1624:    def test_off_ledger_candidate_refuses_even_beside_registered_pair(self) -> None:
impl/d117-u1-ledger-session:tests/test_calibration_bracketing.py:1625:        candidates = [
impl/d117-u1-ledger-session:tests/test_calibration_bracketing.py:1626:            self.candidate("pre", 99.0, "0.025"),
impl/d117-u1-ledger-session:tests/test_calibration_bracketing.py:1627:            self.candidate("post", 111.0, "0.026"),
impl/d117-u1-ledger-session:tests/test_calibration_bracketing.py:1629:        snapshot, registered = _fixture_snapshot(candidates)
impl/d117-u1-ledger-session:tests/test_calibration_bracketing.py:1631:            self.candidate("unregistered-copy", 105.0, "0.0255"),
impl/d117-u1-ledger-session:tests/test_calibration_bracketing.py:1665:                self.candidate("pre", 99.0, "0.020"),
impl/d117-u1-ledger-session:tests/test_calibration_bracketing.py:1666:                self.candidate("post", 111.0, "0.020"),
impl/d117-u1-ledger-session:tests/test_calibration_bracketing.py:1684:        candidates = []
impl/d117-u1-ledger-session:tests/test_calibration_bracketing.py:1686:            candidates.append(
impl/d117-u1-ledger-session:tests/test_calibration_bracketing.py:1688:                    self.candidate(
impl/d117-u1-ledger-session:tests/test_calibration_bracketing.py:1704:            candidates.append(
impl/d117-u1-ledger-session:tests/test_calibration_bracketing.py:1706:                    self.candidate(f"new-{index}", 200.0 + index, "0.025"),
impl/d117-u1-ledger-session:tests/test_calibration_bracketing.py:1715:        snapshot, registered = _fixture_snapshot(candidates)
impl/d117-u1-ledger-session:tests/test_calibration_bracketing.py:1734:        candidates = [
impl/d117-u1-ledger-session:tests/test_calibration_bracketing.py:1735:            self.candidate("pre", 99.0, "0.025"),
impl/d117-u1-ledger-session:tests/test_calibration_bracketing.py:1736:            self.candidate("post", 111.0, "0.026"),
impl/d117-u1-ledger-session:tests/test_calibration_bracketing.py:1789:                    candidates,
impl/d117-u1-ledger-session:tests/test_calibration_bracketing.py:1851:                self.candidate("pre", 99.0, "0.025", bindings=changed),
impl/d117-u1-ledger-session:tests/test_calibration_bracketing.py:1852:                self.candidate("post", 111.0, "0.026", bindings=changed),
impl/d117-u1-ledger-session:tests/test_calibration_bracketing.py:1877:                    self.candidate("pre", 99.0, "0.025"),
impl/d117-u1-ledger-session:tests/test_calibration_bracketing.py:1878:                    self.candidate("post", 111.0, "0.026"),
impl/d117-u1-ledger-session:tests/test_calibration_bracketing.py:1893:    def test_hash_rekeyed_candidate_cannot_bypass_binding_authentication(self) -> None:
impl/d117-u1-ledger-session:tests/test_calibration_bracketing.py:1946:            directory = root / "instrument_validation" / "candidate"
impl/d117-u1-ledger-session:tests/test_calibration_bracketing.py:1979:                candidate = load_calibration_candidate(
impl/d117-u1-ledger-session:tests/test_calibration_bracketing.py:1982:                self.assertIsNotNone(candidate)
impl/d117-u1-ledger-session:tests/test_calibration_bracketing.py:1983:                self.assertEqual(candidate.b_fiducial_s, "0.02")
impl/d117-u1-ledger-session:tests/test_calibration_bracketing.py:1987:                    load_calibration_candidate(directory, runs_root=root)
impl/d117-u1-ledger-session:tests/test_calibration_ledger.py:22:from scripts import reserve_calibration_window_bracket as bracket_session_cli
impl/d117-u1-ledger-session:tests/test_calibration_ledger.py:44:    abort_bracket_session,
impl/d117-u1-ledger-session:tests/test_calibration_ledger.py:45:    append_bracket_session_receipt,
impl/d117-u1-ledger-session:tests/test_calibration_ledger.py:55:    finalize_bracket_session_slot,
impl/d117-u1-ledger-session:tests/test_calibration_ledger.py:84:class CalibrationLedgerTests(unittest.TestCase):
impl/d117-u1-ledger-session:tests/test_calibration_ledger.py:211:    def _open_bracket_session(self, session_id: str = "session-alpha"):
impl/d117-u1-ledger-session:tests/test_calibration_ledger.py:212:        return append_bracket_session_receipt(
impl/d117-u1-ledger-session:tests/test_calibration_ledger.py:248:    def _finalize_bracket_slot(self, session_id: str, slot: str):
impl/d117-u1-ledger-session:tests/test_calibration_ledger.py:255:        return finalize_bracket_session_slot(
impl/d117-u1-ledger-session:tests/test_calibration_ledger.py:387:        self._open_bracket_session()
impl/d117-u1-ledger-session:tests/test_calibration_ledger.py:403:                finalize_bracket_session_slot(
impl/d117-u1-ledger-session:tests/test_calibration_ledger.py:423:            "calibration_ledger_bracket_session_open",
impl/d117-u1-ledger-session:tests/test_calibration_ledger.py:427:        abort_bracket_session(
impl/d117-u1-ledger-session:tests/test_calibration_ledger.py:451:        self.assertEqual(recovered.bracket_sessions[0].state, "aborted")
impl/d117-u1-ledger-session:tests/test_calibration_ledger.py:589:    def test_bracket_session_happy_path_reserves_two_slots_under_one_pin(self) -> None:
impl/d117-u1-ledger-session:tests/test_calibration_ledger.py:590:        capability = self._open_bracket_session()
impl/d117-u1-ledger-session:tests/test_calibration_ledger.py:598:        pre = self._finalize_bracket_slot("session-alpha", "pre")
impl/d117-u1-ledger-session:tests/test_calibration_ledger.py:601:        post = self._finalize_bracket_slot("session-alpha", "post")
impl/d117-u1-ledger-session:tests/test_calibration_ledger.py:617:        session = snapshot.bracket_session_by_id["session-alpha"]
impl/d117-u1-ledger-session:tests/test_calibration_ledger.py:619:        self.assertEqual(set(session.finalized_slots), {"pre", "post"})
impl/d117-u1-ledger-session:tests/test_calibration_ledger.py:621:    def test_bracket_session_refuses_reordered_duplicate_and_conflicting_slots(
impl/d117-u1-ledger-session:tests/test_calibration_ledger.py:624:        self._open_bracket_session()
impl/d117-u1-ledger-session:tests/test_calibration_ledger.py:627:            finalize_bracket_session_slot(
impl/d117-u1-ledger-session:tests/test_calibration_ledger.py:639:        self._finalize_bracket_slot("session-alpha", "pre")
impl/d117-u1-ledger-session:tests/test_calibration_ledger.py:641:            self._finalize_bracket_slot("session-alpha", "pre")
impl/d117-u1-ledger-session:tests/test_calibration_ledger.py:646:            finalize_bracket_session_slot(
impl/d117-u1-ledger-session:tests/test_calibration_ledger.py:660:        capability = self._open_bracket_session()
impl/d117-u1-ledger-session:tests/test_calibration_ledger.py:665:        pre = self._finalize_bracket_slot("session-alpha", "pre")
impl/d117-u1-ledger-session:tests/test_calibration_ledger.py:674:        self._open_bracket_session()
impl/d117-u1-ledger-session:tests/test_calibration_ledger.py:676:        finalize_bracket_session_slot(
impl/d117-u1-ledger-session:tests/test_calibration_ledger.py:688:        abort_bracket_session(
impl/d117-u1-ledger-session:tests/test_calibration_ledger.py:701:        self.assertEqual(snapshot.bracket_sessions[0].state, "aborted")
impl/d117-u1-ledger-session:tests/test_calibration_ledger.py:729:        self._open_bracket_session()
impl/d117-u1-ledger-session:tests/test_calibration_ledger.py:730:        pre = self._finalize_bracket_slot("session-alpha", "pre")
impl/d117-u1-ledger-session:tests/test_calibration_ledger.py:733:            "calibration_ledger_bracket_session_open",
impl/d117-u1-ledger-session:tests/test_calibration_ledger.py:741:        closure = abort_bracket_session(
impl/d117-u1-ledger-session:tests/test_calibration_ledger.py:747:        self.assertEqual(closure["finalized_slots"], ("pre",))
impl/d117-u1-ledger-session:tests/test_calibration_ledger.py:764:        session = snapshot.bracket_session_by_id["session-alpha"]
impl/d117-u1-ledger-session:tests/test_calibration_ledger.py:766:        self.assertEqual(session.finalized_slots["pre"].receipt_digest, pre["receipt_digest"])
impl/d117-u1-ledger-session:tests/test_calibration_ledger.py:768:            abort_bracket_session(
impl/d117-u1-ledger-session:tests/test_calibration_ledger.py:774:    def test_bracket_session_open_requires_exact_committed_physical_head(self) -> None:

exec
/bin/zsh -lc "git show impl/d117-u1-ledger-session:joulewise/calibration_ledger.py | sed -n '35,140p;210,380p;500,760p;1230,1510p'; git show impl/d117-u1-ledger-session:joulewise/calibration_bracketing.py | sed -n '35,125p;520,735p;920,1040p;1180,1510p;1590,1725p'" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Any, BinaryIO

from joulewise.powermetrics_fiducial import V2_BINDING_FIELDS


LEDGER_SCHEMA = "joulewise.calibration_observation_ledger.v1"
RECEIPT_SCHEMA = "joulewise.calibration_observation_receipt.v1"
BRACKET_SESSION_SCHEMA = "joulewise.calibration_window_bracket_session.v1"
BRACKET_SESSION_OPEN_EVENT = "bracket-session-open"
BRACKET_SESSION_SLOT_CLAIM_EVENT = "bracket-session-slot-claim"
BRACKET_SESSION_FINALIZATION_EVENT = "bracket-session-slot-finalization"
BRACKET_SESSION_ABORT_EVENT = "bracket-session-abort"
BRACKET_SESSION_SLOTS = ("pre", "post")
APPEND_JOURNAL_SCHEMA = "joulewise.calibration_ledger_append_journal.v1"
APPEND_RECOVERY_SCHEMA = "joulewise.calibration_ledger_append_recovery.v1"
HISTORICAL_IMPORT_TABLE_SCHEMA = (
    "joulewise.calibration_historical_import_table.v1"
)
HISTORICAL_IMPORT_CUSTODY_MANIFEST_SCHEMA = (
    "joulewise.calibration_historical_import_custody_manifest.v1"
)
HISTORICAL_IMPORT_EVENT_PREFIX = "historical-import-v1"
HISTORICAL_IMPORT_RESERVATION_EVENT = (
    f"{HISTORICAL_IMPORT_EVENT_PREFIX}-reservation"
)
HISTORICAL_IMPORT_FINALIZATION_EVENT = (
    f"{HISTORICAL_IMPORT_EVENT_PREFIX}-finalization"
)
GENESIS_DIGEST = "0" * 64
REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LEDGER_PATH = REPO_ROOT / "runs" / "calibration_observation_ledger.jsonl"
DEFAULT_HEAD_PIN_PATH = (
    REPO_ROOT / "configs" / "calibration" / "calibration_ledger_head.json"
)

IDENTITY_EPOCH_FIELDS = (
    "os_build",
    "hardware_model",
    "power_policy",
    "sampling_interval_ms",
    "estimator_revision",
    "pulse_protocol_id",
)
T1_FIELDS = tuple(V2_BINDING_FIELDS)
FINAL_DISPOSITIONS = frozenset(
    {"valid", "systematic-invalid", "ordinary-invalid", "abandoned"}
)
HISTORICAL_IMPORT_DISPOSITIONS = frozenset(
    {"valid", "systematic-invalid", "ordinary-invalid"}
)
ALL_DISPOSITIONS = FINAL_DISPOSITIONS | {"pending"}
CONTENT_ID_ARTIFACTS = (
    "instrument_evidence.json",
    "manifest.json",
)
GOVERNED_ARTIFACTS = (
    "raw/powermetrics.plist",
    "events.jsonl",
    "power_trace.csv",
    "instrument_evidence.json",
    "manifest.json",
)
MANIFEST_BOUND_ARTIFACTS = tuple(
    name for name in GOVERNED_ARTIFACTS if name != "manifest.json"
)
EVIDENCE_BOUND_ARTIFACTS = (
    "raw/powermetrics.plist",
    "events.jsonl",
    "power_trace.csv",
)
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")

# Stable refusal taxonomy.  Consumers propagate these exact spellings into
# claim barriers; no malformed or unresolved history is silently omitted.
REFUSAL_TAXONOMY: Mapping[str, str] = MappingProxyType(
    {
        "calibration_ledger_missing": "the pinned non-genesis ledger is absent",
        "calibration_ledger_malformed": "ledger, receipt, or head-pin schema is malformed",
        "calibration_ledger_chain_conflict": "sequence or predecessor linkage is not one linear chain",
        "calibration_ledger_attempt_conflict": "an attempt has duplicate or conflicting state transitions",
        "calibration_ledger_bracket_session_conflict": "a bracket session has duplicate, reordered, or conflicting state transitions",
        "calibration_ledger_bracket_slot_claimed": "a bracket session slot already has an exclusive writer claim",
        "calibration_ledger_bracket_session_open": "a bracket session has not finalized both slots or recorded a governed abort",
        "calibration_ledger_content_conflict": "one content identity has conflicting authenticated classifications",
        "calibration_ledger_pending": "at least one reservation is unresolved",
        "calibration_ledger_head_uncommitted": "the head pin differs from the Git HEAD bytes",
        "calibration_ledger_head_mismatch": "the physical head differs from the committed pin",
        "calibration_ledger_rollback": "the physical ledger is a proper prefix of the pinned head",
        "calibration_ledger_recovery_required": "the final ledger line is a journal-authenticated torn append requiring governed recovery",
        "calibration_ledger_baseline_missing": "the acceptance cutoff is not in the current chain",
        "calibration_ledger_custody_invalid": "receipt-bound evidence bytes are absent or hash-invalid",
        "calibration_ledger_snapshot_required": "claim evaluation did not receive one immutable snapshot",
        "calibration_ledger_off_ledger_artifact": "a calibration artifact is not registered in the snapshot",
        "calibration_observation_unclassifiable": "a governed observation has no ruled disposition",
    }
)


class CalibrationLedgerError(ValueError):
    """A writer-side ledger operation cannot preserve the D-109 contract."""




@dataclass(frozen=True)
class LedgerObservation:
    sequence: int
    receipt_digest: str
    attempt_id: str
    content_id: str | None
    artifact_sha256: Mapping[str, str]
    identity_epoch: Mapping[str, Any]
    t1_bindings: Mapping[str, Any]
    capture_wall_time_s: str | None
    exact_bound_lexeme_s: str | None
    disposition: str
    custody_locator: str
    observation_kind: str = "live-capture"
    bracket_session_id: str | None = None
    bracket_slot: str | None = None
    bracket_window_id: str | None = None
    bracket_plan_id: str | None = None
    bracket_plan_sha256: str | None = None
    bracket_evidence_root_id: str | None = None
    bracket_runs_root: str | None = None

    @property
    def classification_disposition(self) -> str:
        """Map the writer terminal state onto the R2 observation schema."""

        return (
            "unresolved" if self.disposition == "abandoned" else self.disposition
        )

    @property
    def is_historical_import(self) -> bool:
        return self.observation_kind == "historical-import"


@dataclass(frozen=True)
class CalibrationLedgerSnapshot:
    """One immutable, fully checked view threaded through an evaluation."""

    ledger_schema: str
    ledger_path: Path
    head_sequence: int
    head_digest: str
    receipts: tuple[Mapping[str, Any], ...]
    observations: tuple[LedgerObservation, ...]
    refusal_reasons: tuple[str, ...]
    bracket_sessions: tuple["CalibrationBracketSession", ...] = ()
    baseline_sequence: int | None = None
    baseline_digest: str | None = None
    committed_head_sequence: int | None = None
    committed_head_digest: str | None = None

    @property
    def valid(self) -> bool:
        return not self.refusal_reasons

    @property
    def observation_by_attempt(self) -> Mapping[str, LedgerObservation]:
        return MappingProxyType(
            {observation.attempt_id: observation for observation in self.observations}
        )

    @property
    def bracket_session_by_id(self) -> Mapping[str, "CalibrationBracketSession"]:
        return MappingProxyType(
            {session.session_id: session for session in self.bracket_sessions}
        )

    @property
    def is_governed_open_bracket_extension(self) -> bool:
        """Whether the physical/pin gap is exactly one reserved open session."""

        allowed = {
            "calibration_ledger_bracket_session_open",
            "calibration_ledger_head_mismatch",
        }
        if (
            set(self.refusal_reasons) != allowed
            or self.committed_head_sequence is None
            or self.committed_head_digest is None
        ):
            return False
        open_sessions = [
            session for session in self.bracket_sessions if session.state == "open"
        ]
        if len(open_sessions) != 1:
            return False
        session = open_sessions[0]
        if session.capability_sequence != self.committed_head_sequence + 1:
            return False
        tail = self.receipts[self.committed_head_sequence :]
        return bool(
            tail
            and tail[0].get("event") == BRACKET_SESSION_OPEN_EVENT
            and tail[0].get("predecessor_digest") == self.committed_head_digest
            and all(row.get("session_id") == session.session_id for row in tail)
        )

    @property
    def observations_by_content(self) -> Mapping[str, tuple[LedgerObservation, ...]]:
        grouped: dict[str, list[LedgerObservation]] = {}
        for observation in self.observations:
            if observation.content_id is not None:
                grouped.setdefault(observation.content_id, []).append(observation)
        return MappingProxyType(
            {key: tuple(value) for key, value in sorted(grouped.items())}
        )

    def post_cutoff_live_observations(
        self, cutoff_sequence: int
    ) -> tuple[LedgerObservation, ...]:
        """Return only fresh live-capture observations after ``cutoff_sequence``.

        Historical bootstrap finalizations are deliberately excluded even
        when a caller compares them with the genesis sequence-zero cutoff.
        """

        if (
            isinstance(cutoff_sequence, bool)
            or not isinstance(cutoff_sequence, int)
            or cutoff_sequence < 0
        ):
            raise CalibrationLedgerError("cutoff_sequence must be nonnegative")
        return tuple(
            observation
            for observation in self.observations
            if observation.sequence > cutoff_sequence
            and not observation.is_historical_import
        )


@dataclass(frozen=True)
class CalibrationBracketSession:
    """Authenticated state of one prospectively reserved two-slot window."""

    session_id: str
    window_id: str
    plan_id: str
    plan_sha256: str
    evidence_root_id: str
    runs_root: str
    capability_receipt_digest: str
    capability_sequence: int
    slot_attempt_ids: Mapping[str, str]
    state: str
    finalized_slots: Mapping[str, LedgerObservation]
    abort_receipt_digest: str | None = None
    abort_reason: str | None = None


@dataclass(frozen=True)
class HistoricalImportPlan:
    """Deterministic, authenticated genesis bootstrap prepared in memory."""

    receipts: tuple[Mapping[str, Any], ...]
    final_sequence: int
    head_digest: str
    head_pin: Mapping[str, Any]
    disposition_table_sha256: str
    custody_manifest_sha256: str

    @property
    def ledger_bytes(self) -> bytes:
        return b"".join(canonical_json_bytes(row) + b"\n" for row in self.receipts)


class HistoricalImportDurabilityUncertain(CalibrationLedgerError):
    """The import committed, but its parent-directory fsync did not confirm."""

def _valid_chain_fields(receipt: Mapping[str, Any], schema: str) -> bool:
    sequence = receipt.get("sequence")
    return (
        receipt.get("schema_version") == schema
        and receipt.get("ledger_schema") == LEDGER_SCHEMA
        and not isinstance(sequence, bool)
        and isinstance(sequence, int)
        and sequence >= 1
        and _is_sha256(receipt.get("predecessor_digest"))
        and _is_sha256(receipt.get("receipt_digest"))
        and receipt.get("receipt_digest") == _receipt_digest(receipt)
    )


def _valid_session_identity(receipt: Mapping[str, Any]) -> bool:
    return (
        all(
            isinstance(receipt.get(field), str) and bool(receipt.get(field))
            for field in (
                "session_id",
                "window_id",
                "plan_id",
                "evidence_root_id",
                "runs_root",
            )
        )
        and _is_sha256(receipt.get("plan_sha256"))
    )


def _valid_session_slot_reservation(slot: object, expected_role: str) -> bool:
    if not isinstance(slot, Mapping) or set(slot) != _SESSION_SLOT_KEYS:
        return False
    epoch = slot.get("identity_epoch")
    t1 = slot.get("t1_bindings")
    return (
        isinstance(slot.get("attempt_id"), str)
        and bool(slot.get("attempt_id"))
        and isinstance(slot.get("custody_locator"), str)
        and bool(slot.get("custody_locator"))
        and slot.get("expected_time_role") == expected_role
        and isinstance(epoch, Mapping)
        and set(epoch) == set(IDENTITY_EPOCH_FIELDS)
        and all(epoch.get(field) not in (None, "") for field in IDENTITY_EPOCH_FIELDS)
        and isinstance(t1, Mapping)
        and set(t1) == set(T1_FIELDS)
        and all(t1.get(field) not in (None, "") for field in T1_FIELDS)
    )


def _valid_session_receipt_shape(receipt: Mapping[str, Any]) -> bool:
    event = receipt.get("event")
    expected_keys = {
        BRACKET_SESSION_OPEN_EVENT: _SESSION_OPEN_KEYS,
        BRACKET_SESSION_SLOT_CLAIM_EVENT: _SESSION_SLOT_CLAIM_KEYS,
        BRACKET_SESSION_FINALIZATION_EVENT: _SESSION_FINALIZATION_KEYS,
        BRACKET_SESSION_ABORT_EVENT: _SESSION_ABORT_KEYS,
    }.get(event)
    if (
        expected_keys is None
        or set(receipt) != expected_keys
        or not _valid_chain_fields(receipt, BRACKET_SESSION_SCHEMA)
        or not _valid_session_identity(receipt)
    ):
        return False
    if event == BRACKET_SESSION_OPEN_EVENT:
        slots = receipt.get("slots")
        return (
            isinstance(slots, Mapping)
            and set(slots) == set(BRACKET_SESSION_SLOTS)
            and all(
                _valid_session_slot_reservation(slots.get(role), role)
                for role in BRACKET_SESSION_SLOTS
            )
            and slots["pre"]["attempt_id"] != slots["post"]["attempt_id"]
        )
    if event == BRACKET_SESSION_SLOT_CLAIM_EVENT:
        return (
            receipt.get("slot") in BRACKET_SESSION_SLOTS
            and isinstance(receipt.get("attempt_id"), str)
            and bool(receipt.get("attempt_id"))
            and isinstance(receipt.get("claim_id"), str)
            and bool(receipt.get("claim_id"))
        )
    if event == BRACKET_SESSION_ABORT_EVENT:
        finalized = receipt.get("finalized_slots")
        unused = receipt.get("unused_slots")
        reason = receipt.get("reason")
        return (
            isinstance(finalized, Sequence)
            and not isinstance(finalized, (str, bytes))
            and isinstance(unused, Sequence)
            and not isinstance(unused, (str, bytes))
            and all(slot in BRACKET_SESSION_SLOTS for slot in (*finalized, *unused))
            and len(set((*finalized, *unused))) == len(finalized) + len(unused)
            and set((*finalized, *unused)) == set(BRACKET_SESSION_SLOTS)
            and isinstance(reason, str)
            and bool(reason)
        )
    disposition = receipt.get("disposition")
    artifacts = receipt.get("artifact_sha256")
    epoch = receipt.get("identity_epoch")
    t1 = receipt.get("t1_bindings")
    capture = receipt.get("capture_wall_time_s")
    bound = receipt.get("exact_bound_lexeme_s")
    content_id = receipt.get("content_id")
    if (
        receipt.get("slot") not in BRACKET_SESSION_SLOTS
        or not isinstance(receipt.get("attempt_id"), str)
        or not receipt.get("attempt_id")
        or disposition not in FINAL_DISPOSITIONS
        or not isinstance(receipt.get("custody_locator"), str)
        or not isinstance(artifacts, Mapping)
        or any(
            not isinstance(name, str) or not name or not _is_sha256(digest)
            for name, digest in artifacts.items()
        )
        or not isinstance(epoch, Mapping)
        or set(epoch) != set(IDENTITY_EPOCH_FIELDS)
        or not isinstance(t1, Mapping)
        or set(t1) != set(T1_FIELDS)
        or (capture is not None and not isinstance(capture, str))
        or (bound is not None and not isinstance(bound, str))
        or (content_id is not None and not _is_sha256(content_id))
    ):
        return False
    if disposition == "abandoned":
        return content_id == content_id_from_artifact_hashes(artifacts)
    return (
        content_id is not None
        and content_id_from_artifact_hashes(artifacts) == content_id
        and bool(receipt.get("custody_locator"))
        and all(epoch.get(field) not in (None, "") for field in IDENTITY_EPOCH_FIELDS)
        and all(t1.get(field) not in (None, "") for field in T1_FIELDS)
        and capture is not None
    )


def _valid_receipt_shape(receipt: object) -> bool:
    if not isinstance(receipt, Mapping):
        return False
    if receipt.get("schema_version") == BRACKET_SESSION_SCHEMA:
        return _valid_session_receipt_shape(receipt)
    sequence = receipt.get("sequence")
    event = receipt.get("event")
    expected_keys = (
        _HISTORICAL_IMPORT_RESERVATION_KEYS
        if event == HISTORICAL_IMPORT_RESERVATION_EVENT
        else _RECEIPT_KEYS
    )
    if set(receipt) != expected_keys:
        return False
    disposition = receipt.get("disposition")
    artifacts = receipt.get("artifact_sha256")
    epoch = receipt.get("identity_epoch")
    t1 = receipt.get("t1_bindings")
    capture = receipt.get("capture_wall_time_s")
    bound = receipt.get("exact_bound_lexeme_s")
    if (
        receipt.get("schema_version") != RECEIPT_SCHEMA
        or receipt.get("ledger_schema") != LEDGER_SCHEMA
        or isinstance(sequence, bool)
        or not isinstance(sequence, int)
        or sequence < 1
        or not _is_sha256(receipt.get("predecessor_digest"))
        or event
        not in {
            "reservation",
            "finalization",
            HISTORICAL_IMPORT_RESERVATION_EVENT,
            HISTORICAL_IMPORT_FINALIZATION_EVENT,
        }
        or not isinstance(receipt.get("attempt_id"), str)
        or not receipt.get("attempt_id")
        or disposition not in ALL_DISPOSITIONS
        or not isinstance(receipt.get("custody_locator"), str)
        or not isinstance(artifacts, Mapping)
        or any(
            not isinstance(name, str) or not name or not _is_sha256(digest)
            for name, digest in artifacts.items()
        )
        or not isinstance(epoch, Mapping)
        or set(epoch) != set(IDENTITY_EPOCH_FIELDS)
        or not isinstance(t1, Mapping)
        or set(t1) != set(T1_FIELDS)
        or (capture is not None and not isinstance(capture, str))
        or (bound is not None and not isinstance(bound, str))
        or not _is_sha256(receipt.get("receipt_digest"))
        or receipt.get("receipt_digest") != _receipt_digest(receipt)
    ):
        return False
    content_id = receipt.get("content_id")
    if content_id is not None and not _is_sha256(content_id):
        return False
    if event in {"reservation", HISTORICAL_IMPORT_RESERVATION_EVENT}:
        historical_input_sha256 = receipt.get(
            _HISTORICAL_IMPORT_INPUT_SHA256_KEY
        )
        return (
            disposition == "pending"
            and content_id is None
            and not artifacts
            and capture is None
            and bound is None
            and all(
                epoch.get(field) not in (None, "")
                for field in IDENTITY_EPOCH_FIELDS
            )
            and all(t1.get(field) not in (None, "") for field in T1_FIELDS)
            and (
                event != HISTORICAL_IMPORT_RESERVATION_EVENT
                or isinstance(historical_input_sha256, Mapping)
                and set(historical_input_sha256)
                == _HISTORICAL_IMPORT_INPUT_SHA256_KEYS
                and all(
                    _is_sha256(historical_input_sha256.get(name))
                    for name in _HISTORICAL_IMPORT_INPUT_SHA256_KEYS
                )
            )
        )
    if disposition not in FINAL_DISPOSITIONS:
        return False
    if disposition == "abandoned":
        # R1 retains the terminal writer state as ``abandoned`` while R2
        # classifies it as unresolved.  When canonical primary bytes exist,
        # preserve their authentic content identity; a partial/no-content
        # attempt remains representable with a null content id.
        return content_id == content_id_from_artifact_hashes(artifacts)
    if (
        content_id is None
        or content_id_from_artifact_hashes(artifacts) != content_id
        or not receipt.get("custody_locator")
        or any(epoch.get(field) in (None, "") for field in IDENTITY_EPOCH_FIELDS)
        or any(t1.get(field) in (None, "") for field in T1_FIELDS)
        or capture is None
    ):
        return False
    return True


def _head_pin(value: object) -> tuple[int, str] | None:
    if not isinstance(value, Mapping) or set(value) != {
        "sequence",
        "head_digest",
        "ledger_schema",
    }:
        return None
    sequence = value.get("sequence")
    digest = value.get("head_digest")
    if (
        value.get("ledger_schema") != LEDGER_SCHEMA
        or isinstance(sequence, bool)
        or not isinstance(sequence, int)
        or sequence < 0
        or not _is_sha256(digest)
        or (sequence == 0 and digest != GENESIS_DIGEST)
    ):
        return None
    return sequence, str(digest)


    return set()


def load_calibration_ledger_snapshot(
    ledger_path: Path = DEFAULT_LEDGER_PATH,
    head_pin_path: Path = DEFAULT_HEAD_PIN_PATH,
    *,
    baseline_sequence: int | None = None,
    baseline_digest: str | None = None,
    require_committed_pin: bool = True,
    verify_custody: bool = True,
    repo_root: Path = REPO_ROOT,
) -> CalibrationLedgerSnapshot:
    """Load, authenticate, and freeze exactly one ledger snapshot.

    A proper physical prefix of the pin is classified explicitly as rollback;
    any other physical/pinned disagreement is a stale-head mismatch.  The
    baseline must occur at its exact sequence in the same complete chain.
    This closes workflow omission, unregistered evidence, and rollback or
    stale-head consumption; it does not defend against a malicious trusted
    writer or a rewrite of both Git and the full ledger history.
    """

    ledger_path = Path(ledger_path)
    head_pin_path = Path(head_pin_path)
    reasons: set[str] = set()
    try:
        pin_raw = head_pin_path.read_bytes()
        pin_value = json.loads(pin_raw)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        pin_raw = b""
        pin_value = None
    pin = _head_pin(pin_value)
    if pin is None:
        reasons.add("calibration_ledger_malformed")
        pinned_sequence, pinned_digest = 0, GENESIS_DIGEST
    else:
        pinned_sequence, pinned_digest = pin
    try:
        raw = ledger_path.read_bytes()
    except OSError:
        raw = b""
        if pinned_sequence > 0:
            reasons.add("calibration_ledger_missing")
    genesis_development_bootstrap = (
        pinned_sequence == 0
        and pinned_digest == GENESIS_DIGEST
        and not raw
        and not ledger_path.exists()
    )
    if (
        require_committed_pin
        # The checked-in fixture starts at genesis.  Before its first commit,
        # an absent physical ledger cannot license a claim (there are no
        # endpoints); permitting this development-only empty view avoids a
        # circular "commit before tests" bootstrap. Any physical byte or any
        # non-genesis pin remains strictly commit-authenticated.
        and not genesis_development_bootstrap
        and _committed_pin_bytes(head_pin_path, repo_root) != pin_raw
    ):
        reasons.add("calibration_ledger_head_uncommitted")
    append_journal, malformed_journal = _read_append_journal(ledger_path)
    receipts, parse_reasons = _parse_ledger(
        raw,
        append_journal=append_journal,
    )
    if malformed_journal:
        parse_reasons.add("calibration_ledger_malformed")
    reasons.update(parse_reasons)
    physical_sequence = len(receipts)
    physical_digest = (
        str(receipts[-1]["receipt_digest"]) if receipts else GENESIS_DIGEST
    )
    if (physical_sequence, physical_digest) != (pinned_sequence, pinned_digest):
        if physical_sequence < pinned_sequence:
            reasons.add("calibration_ledger_rollback")
        else:
            reasons.add("calibration_ledger_head_mismatch")
    if baseline_sequence is not None or baseline_digest is not None:
        if (
            isinstance(baseline_sequence, bool)
            or not isinstance(baseline_sequence, int)
            or baseline_sequence < 0
            or not _is_sha256(baseline_digest)
        ):
            reasons.add("calibration_ledger_baseline_missing")
        else:
            in_chain = (
                baseline_digest == GENESIS_DIGEST
                if baseline_sequence == 0
                else baseline_sequence <= len(receipts)
                and receipts[baseline_sequence - 1]["receipt_digest"]
                == baseline_digest
            )
            if not in_chain or baseline_sequence > pinned_sequence:
                reasons.add("calibration_ledger_baseline_missing")
    observations, bracket_sessions, state_reasons = _attempts_and_observations(
        receipts
    )
    reasons.update(state_reasons)
    if verify_custody:
        custody_observations = list(observations)
        custody_attempt_ids = {observation.attempt_id for observation in observations}
        for session in bracket_sessions:
            custody_observations.extend(
                observation
                for observation in session.finalized_slots.values()
                if observation.attempt_id not in custody_attempt_ids
            )
        reasons.update(_custody_reasons(custody_observations, repo_root))
    return CalibrationLedgerSnapshot(
        ledger_schema=LEDGER_SCHEMA,
        ledger_path=ledger_path,
        head_sequence=physical_sequence,
        head_digest=physical_digest,
        receipts=tuple(_frozen_mapping(receipt) for receipt in receipts),
        observations=tuple(observations),
        refusal_reasons=tuple(sorted(reasons)),
        bracket_sessions=tuple(bracket_sessions),
        baseline_sequence=baseline_sequence,
        baseline_digest=baseline_digest,
        committed_head_sequence=pinned_sequence,
        committed_head_digest=pinned_digest,
    )


def _new_receipt(
    *,
    sequence: int,
    predecessor_digest: str,
    event: str,
    attempt_id: str,
    content_id: str | None,
    artifacts: Mapping[str, str],
    identity_epoch: Mapping[str, Any] | None,
    t1_bindings: Mapping[str, Any] | None,
    capture_wall_time_s: str | None,
    exact_bound_lexeme_s: str | None,
    disposition: str,
    custody_locator: str,
    historical_import_input_sha256: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    receipt: dict[str, Any] = {
        "schema_version": RECEIPT_SCHEMA,
        "ledger_schema": LEDGER_SCHEMA,
        "sequence": sequence,
        "predecessor_digest": predecessor_digest,
        "event": event,
        "attempt_id": attempt_id,
        "content_id": content_id,
        "artifact_sha256": dict(sorted(artifacts.items())),
        "identity_epoch": _normalized_vector(identity_epoch, IDENTITY_EPOCH_FIELDS),
        "t1_bindings": _normalized_vector(t1_bindings, T1_FIELDS),
        "capture_wall_time_s": capture_wall_time_s,
        "exact_bound_lexeme_s": exact_bound_lexeme_s,
        "disposition": disposition,
        "custody_locator": custody_locator,
    }
    if historical_import_input_sha256 is not None:
        receipt[_HISTORICAL_IMPORT_INPUT_SHA256_KEY] = dict(
            sorted(historical_import_input_sha256.items())
        )
    receipt["receipt_digest"] = _receipt_digest(receipt)
    return receipt


def _new_bracket_session_record(
    *,
    sequence: int,
    predecessor_digest: str,
    event: str,
    session_identity: Mapping[str, Any],
    fields: Mapping[str, Any],
) -> dict[str, Any]:
    receipt = {
        "schema_version": BRACKET_SESSION_SCHEMA,
        "ledger_schema": LEDGER_SCHEMA,
        "sequence": sequence,
        "predecessor_digest": predecessor_digest,
        "event": event,
        **{field: session_identity.get(field) for field in _SESSION_IDENTITY_KEYS},
        **dict(fields),
    }
    receipt["receipt_digest"] = _receipt_digest(receipt)
    return receipt


def _json_object_from_bytes(raw: bytes, source: Path) -> Mapping[str, Any]:
    try:
        value = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise CalibrationLedgerError(f"{source}: malformed JSON") from exc
    if not isinstance(value, Mapping):
        raise CalibrationLedgerError(f"{source}: expected a JSON object")
    return value


def _authenticated_json_object(
    raw: bytes,
    expected_sha256: str,
    *,
    label: str,
) -> Mapping[str, Any]:
    if not _is_sha256(expected_sha256):
        raise CalibrationLedgerError(f"expected {label} sha256 is malformed")
    observed = hashlib.sha256(raw).hexdigest()
    if observed != expected_sha256:
        raise CalibrationLedgerError(f"{label} sha256 mismatch")
    return _json_object_from_bytes(raw, Path(label))


def _number_lexemes(raw: bytes, source: Path) -> Mapping[str, Any]:
    try:
        value = json.loads(raw, parse_float=str, parse_int=str)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise CalibrationLedgerError(f"{source}: malformed JSON") from exc
    if not isinstance(value, Mapping):
        raise CalibrationLedgerError(f"{source}: expected a JSON object")
    return value


def _historical_import_table(
    value: Mapping[str, Any],
) -> tuple[dict[str, Any], dict[str, Mapping[str, Any]]]:
    if set(value) != {
        "schema_version",
        "ledger_schema",
        "identity_epoch",
        "members",
    }:
        raise CalibrationLedgerError("historical import table has invalid keys")
    if (
        value.get("schema_version") != HISTORICAL_IMPORT_TABLE_SCHEMA
        or value.get("ledger_schema") != LEDGER_SCHEMA
    ):
        raise CalibrationLedgerError("historical import table schema mismatch")
    epoch = value.get("identity_epoch")
    members = value.get("members")
    if (
        not isinstance(epoch, Mapping)
        or set(epoch) != set(IDENTITY_EPOCH_FIELDS)
        or any(epoch.get(field) in (None, "") for field in IDENTITY_EPOCH_FIELDS)
        or not isinstance(members, list)
        or not members
    ):
        raise CalibrationLedgerError("historical import table is incomplete")

    by_content: dict[str, Mapping[str, Any]] = {}
    attempt_ids: set[str] = set()
    for member in members:
        if not isinstance(member, Mapping) or set(member) != {
            "attempt_id",
            "content_id",
            "artifact_sha256",
            "disposition",
        }:
            raise CalibrationLedgerError("historical import member has invalid keys")
        attempt_id = member.get("attempt_id")
        content_id = member.get("content_id")
        artifacts = member.get("artifact_sha256")
        disposition = member.get("disposition")
        if (
            not isinstance(attempt_id, str)
            or not attempt_id
            or not _is_sha256(content_id)
            or not isinstance(artifacts, Mapping)
            or set(artifacts) != set(GOVERNED_ARTIFACTS)
            or any(not _is_sha256(item) for item in artifacts.values())
            or content_id_from_artifact_hashes(artifacts) != content_id
            or disposition not in HISTORICAL_IMPORT_DISPOSITIONS
        ):
            raise CalibrationLedgerError("historical import member is malformed")
        if attempt_id in attempt_ids:
            raise CalibrationLedgerError(
                "historical import attempt_id collision; content_id tiebreak is "
                "diagnostic only"
            )
        if str(content_id) in by_content:
            raise CalibrationLedgerError("historical import content_id is duplicated")
        attempt_ids.add(attempt_id)
        by_content[str(content_id)] = member
    protocol_pulse_count,
    protocol_sha256,
    verify_stored_evidence_physics,
)
from joulewise.schemas import CalibrationBracketingPolicy

BRACKET_SCHEMA = "joulewise.instrument_calibration_bracket.v1"
BRACKET_BINDING_SCHEMA = "joulewise.calibration_bracket_binding.v1"
ACCEPTANCE_BOUND_SCHEMA = "joulewise.calibration_acceptance_bound.v2"
ACCEPTANCE_FIXTURE_SCHEMA = (
    "joulewise.calibration_acceptance_bound.v2.fixture.v1"
)
ACCEPTANCE_EVALUATION_SCHEMA = "joulewise.calibration_acceptance_evaluation.v2"
DEFAULT_ACCEPTANCE_BOUND_PATH = (
    Path(__file__).resolve().parents[1]
    / "configs"
    / "calibration"
    / "calibration_acceptance_d079_v2.json"
)
DEFAULT_ACCEPTANCE_BOUND_SHA256 = (
    "9a264c57fdc007de473872870f19a5e1c9bd9b11256c25266b0e3e50ebba0ceb"
)
ISSUED_ACCEPTANCE_BOUND_SHA256 = (
    "316113960c596a6f927987dbdf8f2bca4b0cca9ee4a59a540bbd32bba9048985"
)
_REPO_ROOT = Path(__file__).resolve().parents[1]
ESTIMATOR_CODE_PATHS = (
    "joulewise/powermetrics_fiducial.py",
    "joulewise/uncertainty_evidence.py",
    "joulewise/adapters/powermetrics.py",
    "joulewise/reduce.py",
)
ACCEPTANCE_IDENTITY_FIELDS = IDENTITY_EPOCH_FIELDS
_D102_OPERATIVE_VALUES = {
    "bracket_screen_s": "0.010818",
    "preflight_level_screen_s": "0.033558756679900",
    "max_budgetable_excess_s": "0.001275166090593858",
    "maximum_budgetable_drift_s": "0.012093166090593858",
}


@dataclass(frozen=True)
class CalibrationCandidate:
    relative_path: str
    manifest_sha256: str
    evidence_sha256: str
    protocol_id: str
    capture_wall_time_s: float
    # Production authentication stores the source decimal lexeme here.  Float
    # remains accepted only for backwards-compatible synthetic callers; the
    # authenticated loader below never takes that branch.
    b_fiducial_s: Decimal | str | float
    bindings: Mapping[str, Any]
    attempt_id: str | None = None
    content_id: str | None = None
    ledger_receipt_digest: str | None = None
    bracket_session_id: str | None = None
    bracket_slot: str | None = None
    bracket_window_id: str | None = None
    bracket_plan_id: str | None = None
    bracket_plan_sha256: str | None = None
    bracket_evidence_root_id: str | None = None
    bracket_runs_root: str | None = None

    def descriptor(self) -> dict[str, Any]:
        bound = _candidate_decimal(self)
        return {
            "relative_path": self.relative_path,
            "manifest_sha256": self.manifest_sha256,
            "evidence_sha256": self.evidence_sha256,
            "protocol_id": self.protocol_id,
            "capture_wall_time_s": self.capture_wall_time_s,
            # This descriptor is the recorded reducer boundary.  Keep both the
            # exact acceptance lexeme and its explicit binary64 projection.
            "b_fiducial_s": float(bound) if bound is not None else self.b_fiducial_s,
            "b_fiducial_decimal_s": str(bound) if bound is not None else None,
            "attempt_id": self.attempt_id,
            "content_id": self.content_id,
            "ledger_receipt_digest": self.ledger_receipt_digest,
            "bracket_session_id": self.bracket_session_id,
            "bracket_slot": self.bracket_slot,
            "bracket_window_id": self.bracket_window_id,
            "bracket_plan_id": self.bracket_plan_id,
            "bracket_plan_sha256": self.bracket_plan_sha256,
            "bracket_evidence_root_id": self.bracket_evidence_root_id,
            "bracket_runs_root": self.bracket_runs_root,
        }


def _canonical_sha256(value: Mapping[str, Any]) -> str:
    raw = json.dumps(
    "capability_receipt_digest",
    "terminal_head",
    "endpoints",
    "binding_digest",
}
_BRACKET_ENDPOINT_KEYS = {
    "attempt_id",
    "receipt_digest",
    "content_digest",
}


def _binding_core(binding: Mapping[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in binding.items() if key != "binding_digest"}


def build_calibration_bracket_binding(
    ledger_snapshot: CalibrationLedgerSnapshot,
    *,
    session_id: str,
    window_id: str,
    plan_id: str,
    plan_sha256: str,
    evidence_root_id: str,
    runs_root: Path | str,
) -> dict[str, Any]:
    """Bind one frozen window to its exact finalized session endpoints."""

    if not isinstance(ledger_snapshot, CalibrationLedgerSnapshot) or not ledger_snapshot.valid:
        raise ValueError("bracket binding requires a valid pinned ledger snapshot")
    session = ledger_snapshot.bracket_session_by_id.get(session_id)
    expected_identity = (
        window_id,
        plan_id,
        plan_sha256,
        evidence_root_id,
        str(Path(runs_root).absolute()),
    )
    if (
        session is None
        or session.state != "finalized"
        or (
            session.window_id,
            session.plan_id,
            session.plan_sha256,
            session.evidence_root_id,
            session.runs_root,
        )
        != expected_identity
    ):
        raise ValueError("bracket session does not match the frozen window identity")
    pre = session.finalized_slots.get("pre")
    post = session.finalized_slots.get("post")
    if (
        pre is None
        or post is None
        or pre.disposition != "valid"
        or post.disposition != "valid"
        or pre.content_id is None
        or post.content_id is None
        or post.sequence != ledger_snapshot.head_sequence
        or post.receipt_digest != ledger_snapshot.head_digest
    ):
        raise ValueError("bracket session endpoints are not valid at the terminal head")
    binding: dict[str, Any] = {
        "schema_version": BRACKET_BINDING_SCHEMA,
        "ledger_schema": LEDGER_SCHEMA,
        "session_id": session.session_id,
        "window_id": session.window_id,
        "plan_id": session.plan_id,
        "plan_sha256": session.plan_sha256,
        "evidence_root_id": session.evidence_root_id,
        "runs_root": session.runs_root,
        "capability_receipt_digest": session.capability_receipt_digest,
        "terminal_head": {
            "sequence": post.sequence,
            "head_digest": post.receipt_digest,
            "ledger_schema": LEDGER_SCHEMA,
        },
        "endpoints": {
            role: {
                "attempt_id": observation.attempt_id,
                "receipt_digest": observation.receipt_digest,
                "content_digest": observation.content_id,
            }
            for role, observation in (("pre", pre), ("post", post))
        },
    }
    binding["binding_digest"] = _canonical_sha256(binding)
    return binding


def validate_calibration_bracket_binding(
    binding: Mapping[str, Any],
    ledger_snapshot: CalibrationLedgerSnapshot,
    *,
    window_id: str | None = None,
    plan_id: str | None = None,
    plan_sha256: str | None = None,
    evidence_root_id: str | None = None,
    runs_root: Path | str | None = None,
) -> tuple[LedgerObservation, LedgerObservation] | None:
    """Return the exact authenticated pair, or ``None`` on any substitution."""

    if (
        not isinstance(binding, Mapping)
        or set(binding) != _BRACKET_BINDING_KEYS
        or binding.get("schema_version") != BRACKET_BINDING_SCHEMA
        or binding.get("ledger_schema") != LEDGER_SCHEMA
        or not _valid_sha256(binding.get("plan_sha256"))
        or not _valid_sha256(binding.get("capability_receipt_digest"))
        or not _valid_sha256(binding.get("binding_digest"))
        or binding.get("binding_digest") != _canonical_sha256(_binding_core(binding))
        or not isinstance(ledger_snapshot, CalibrationLedgerSnapshot)
        or not ledger_snapshot.valid
    ):
        return None
    if any(
        not isinstance(value, str) or not value
        for value in (window_id, plan_id, plan_sha256, evidence_root_id)
    ) or runs_root is None:
        return None
    expected_runs_root = str(Path(runs_root).absolute())
    for field, expected in (
        ("window_id", window_id),
        ("plan_id", plan_id),
        ("plan_sha256", plan_sha256),
        ("evidence_root_id", evidence_root_id),
        ("runs_root", expected_runs_root),
    ):
        if binding.get(field) != expected:
            return None
    session = ledger_snapshot.bracket_session_by_id.get(str(binding.get("session_id")))
    if (
        session is None
        or session.state != "finalized"
        or binding.get("window_id") != session.window_id
        or binding.get("plan_id") != session.plan_id
        or binding.get("plan_sha256") != session.plan_sha256
        or binding.get("evidence_root_id") != session.evidence_root_id
        or binding.get("runs_root") != session.runs_root
        or binding.get("capability_receipt_digest")
        != session.capability_receipt_digest
    ):
        return None
    terminal = binding.get("terminal_head")
    endpoints = binding.get("endpoints")
    if (
        not isinstance(terminal, Mapping)
        or set(terminal) != {"sequence", "head_digest", "ledger_schema"}
        or terminal.get("ledger_schema") != LEDGER_SCHEMA
        or isinstance(terminal.get("sequence"), bool)
        or not isinstance(terminal.get("sequence"), int)
        or not _valid_sha256(terminal.get("head_digest"))
        or not isinstance(endpoints, Mapping)
        or set(endpoints) != {"pre", "post"}
    ):
        return None
    resolved: list[LedgerObservation] = []
    for role in ("pre", "post"):
        endpoint = endpoints.get(role)
        observation = session.finalized_slots.get(role)
        if (
            not isinstance(endpoint, Mapping)
            or set(endpoint) != _BRACKET_ENDPOINT_KEYS
            or observation is None
            or observation.disposition != "valid"
            or observation.content_id is None
            or endpoint.get("attempt_id") != observation.attempt_id
            or endpoint.get("receipt_digest") != observation.receipt_digest
            or endpoint.get("content_digest") != observation.content_id
        ):
            return None
        resolved.append(observation)
    post = resolved[1]
    if (
        terminal.get("sequence") != post.sequence
        or terminal.get("head_digest") != post.receipt_digest
        or post.sequence > len(ledger_snapshot.receipts)
        or ledger_snapshot.receipts[post.sequence - 1].get("receipt_digest")
        != post.receipt_digest
    ):
        return None
    return resolved[0], resolved[1]


def _binding_evidence_authentic(
    evidence: Mapping[str, Any], bindings: Mapping[str, Any]
) -> bool:
    binding_evidence = evidence.get("binding_evidence")
    binary = (
        binding_evidence.get("powermetrics_binary")
        if isinstance(binding_evidence, Mapping)
        else None
    )
    power_policy = (
        binding_evidence.get("power_policy")
        if isinstance(binding_evidence, Mapping)
        else None
    )
    # Canonical form MUST match the generation (powermetrics_fiducial) and
    # reduce-side consumers byte-for-byte: ensure_ascii=False (delta-review
    # P2 — the ASCII-default form made authentic non-ASCII binding vectors
    # unmatchable as bracket candidates).
    canonical = json.dumps(
        dict(bindings),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
    return bool(
        isinstance(binding_evidence, Mapping)
        and binding_evidence.get("schema_version")
        == "joulewise.instrument_binding_evidence.v1"
        and binding_evidence.get("binding_vector_sha256")
        bracket_slot=observation.bracket_slot,
        bracket_window_id=observation.bracket_window_id,
        bracket_plan_id=observation.bracket_plan_id,
        bracket_plan_sha256=observation.bracket_plan_sha256,
        bracket_evidence_root_id=observation.bracket_evidence_root_id,
        bracket_runs_root=observation.bracket_runs_root,
    )


def discover_calibration_candidates(
    ledger_snapshot: CalibrationLedgerSnapshot,
) -> tuple[CalibrationCandidate, ...]:
    """Enumerate valid endpoints from the sole ledger authority.

    The mechanism closes workflow omission, unregistered evidence, and
    rollback/stale-head consumption; it does not defend against a malicious
    trusted writer or a rewrite of both Git and full ledger history.
    """

    if (
        not isinstance(ledger_snapshot, CalibrationLedgerSnapshot)
        or not ledger_snapshot.valid
        and not ledger_snapshot.is_governed_open_bracket_extension
    ):
        return ()
    finalized_session_ids = {
        session.session_id
        for session in ledger_snapshot.bracket_sessions
        if session.state == "finalized"
    }
    candidates: list[CalibrationCandidate] = []
    for observation in ledger_snapshot.observations:
        if (
            observation.disposition != "valid"
            or observation.is_historical_import
            or observation.bracket_session_id is not None
            and observation.bracket_session_id not in finalized_session_ids
        ):
            continue
        candidate = _candidate_from_observation(observation)
        if candidate is None:
            return ()
        candidates.append(candidate)
    return tuple(candidates)


def _prior_set_matches_import_cutoff_prefix(
    artifact: Mapping[str, Any],
    ledger_snapshot: CalibrationLedgerSnapshot,
) -> bool:
    """Bind issuance prior-set data to the import-marked cutoff prefix."""

    cutoff = artifact["ledger_cutoff"]
    prefix = tuple(
        observation
        for observation in ledger_snapshot.observations
        if observation.sequence <= cutoff["sequence"]
    )
    # The checked-in schema fixture predates issuance and deliberately has a
    # genesis cutoff. Production issuance, or any fixture containing imported
    # prefix rows, must satisfy the exact marker-bound comparison below.
    if not prefix and artifact.get("artifact_role") == "schema_fixture_unissued":
        return True
    if any(not observation.is_historical_import for observation in prefix):
        return False
    catalog = artifact["prior_observation_set"]["epoch_catalog"]
    expected = {
        (
            row["attempt_id"],
            row["content_id"],
            row["disposition"],
            row["epoch_id"],
        )
        for row in artifact["prior_observation_set"]["observations"]
    }
    observed: set[tuple[str, str, str, str]] = set()
    for observation in prefix:
        epoch_ids = [
            epoch_id
            for epoch_id, epoch in catalog.items()
            if dict(epoch) == dict(observation.identity_epoch)
        ]
        if observation.content_id is None or len(epoch_ids) != 1:
            return False
        observed.add(
            (
                observation.attempt_id,
                observation.content_id,
                observation.classification_disposition,
                epoch_ids[0],
            )
        )
    return observed == expected and len(observed) == len(prefix)


def evaluate_calibration_bracket(
    candidates: Sequence[CalibrationCandidate],
    *,
    window_start_s: float,
    window_end_s: float,
    bindings: Mapping[str, Any],
    policy: CalibrationBracketingPolicy,
    acceptance_bound: Mapping[str, Any] | None = None,
    ledger_snapshot: CalibrationLedgerSnapshot | None = None,
    bracket_binding: Mapping[str, Any] | None = None,
    bracket_window_id: str | None = None,
    bracket_plan_id: str | None = None,
    bracket_plan_sha256: str | None = None,
    bracket_evidence_root_id: str | None = None,
    bracket_runs_root: Path | str | None = None,
    _allow_unissued_fixture: bool = False,
) -> tuple[dict[str, Any], tuple[str, ...]]:
    """Select a causal bracket and apply the provenance-bound D-079 budget."""

    result: dict[str, Any] = {
        "schema_version": BRACKET_SCHEMA,
        "policy": {
            "require_bracket": policy.require_bracket,
            "calibration_bracket_max_drift_s": (
                policy.calibration_bracket_max_drift_s
            ),
            "stale_fields": stale_fields,
            "calendar_expiry": None,
        },
        "prospective_rederivation": {
            "observation_rule": prospective["trigger_observation_rule"],
            "candidate_set_boundary": (
                "authenticated_calibration_ledger_snapshot_only"
            ),
            "global_runs_root_scan": False,
            "mandatory_triggers": list(prospective["triggers"]),
            "observed_triggers": [],
        },
        "numeric_semantics": {
            "comparisons": "decimal",
            "reducer_boundary": "binary64_recorded_below",
        },
        "ledger_snapshot": {
            "ledger_schema": ledger_snapshot.ledger_schema,
            "sequence": ledger_snapshot.head_sequence,
            "head_digest": ledger_snapshot.head_digest,
            "baseline_sequence": ledger_snapshot.baseline_sequence,
            "baseline_digest": ledger_snapshot.baseline_digest,
            "load_count": 1,
        },
        "preflight": None,
        "drift": None,
    }
    if stale_fields:
        return result, ("calibration_acceptance_bound_stale",)
    observations_by_attempt = ledger_snapshot.observation_by_attempt
    finalized_session_ids = {
        session.session_id
        for session in ledger_snapshot.bracket_sessions
        if session.state == "finalized"
    }
    registered_valid = {
        (
            observation.attempt_id,
            observation.content_id,
            observation.receipt_digest,
        )
        for observation in ledger_snapshot.observations
        if observation.disposition == "valid"
        and not observation.is_historical_import
        and (
            observation.bracket_session_id is None
            or observation.bracket_session_id in finalized_session_ids
        )
    }
    supplied_valid = {
        (
            candidate.attempt_id,
            candidate.content_id,
            candidate.ledger_receipt_digest,
        )
        for candidate in candidates
    }
    # Even the low-level evaluator requires the complete ledger enumeration.
    # This prevents a caller from narrowing the registered universe to a
    # favorable subset while still passing per-candidate membership checks.
    if supplied_valid != registered_valid or len(candidates) != len(supplied_valid):
        return result, ("calibration_ledger_off_ledger_artifact",)
    for candidate in candidates:
        observation = (
            observations_by_attempt.get(candidate.attempt_id)
            if isinstance(candidate.attempt_id, str)
            else None
        )
        if (
            observation is None
            or observation.disposition != "valid"
            or candidate.content_id != observation.content_id
            or candidate.ledger_receipt_digest != observation.receipt_digest
            or candidate.manifest_sha256
            != observation.artifact_sha256.get("manifest.json")
            or candidate.evidence_sha256
            != observation.artifact_sha256.get("instrument_evidence.json")
            or candidate.bracket_session_id != observation.bracket_session_id
            or candidate.bracket_slot != observation.bracket_slot
            or candidate.bracket_window_id != observation.bracket_window_id
            or candidate.bracket_plan_id != observation.bracket_plan_id
            or candidate.bracket_plan_sha256
            != observation.bracket_plan_sha256
            or candidate.bracket_evidence_root_id
            != observation.bracket_evidence_root_id
            or candidate.bracket_runs_root != observation.bracket_runs_root
        ):
            return result, ("calibration_ledger_off_ledger_artifact",)
    has_session_candidates = any(
        candidate.bracket_session_id is not None for candidate in candidates
    )
    bound_observations: tuple[LedgerObservation, LedgerObservation] | None = None
    if has_session_candidates:
        if (
            bracket_binding is None
            or not all(
                isinstance(value, str) and bool(value)
                for value in (
                    bracket_window_id,
                    bracket_plan_id,
                    bracket_plan_sha256,
                    bracket_evidence_root_id,
                )
            )
            or bracket_runs_root is None
        ):
            return result, ("calibration_bracket_binding_missing",)
        expected_runs_root = str(Path(bracket_runs_root).absolute())
        bound_observations = validate_calibration_bracket_binding(
            bracket_binding,
            ledger_snapshot,
            window_id=bracket_window_id,
            plan_id=bracket_plan_id,
            plan_sha256=bracket_plan_sha256,
            evidence_root_id=bracket_evidence_root_id,
            runs_root=expected_runs_root,
        )
        if bound_observations is None:
            return result, ("calibration_bracket_binding_invalid",)
        result["bracket_binding"] = {
            "schema_version": BRACKET_BINDING_SCHEMA,
            "binding_digest": bracket_binding["binding_digest"],
            "session_id": bracket_binding["session_id"],
            "window_id": bracket_binding["window_id"],
            "plan_id": bracket_binding["plan_id"],
            "plan_sha256": bracket_binding["plan_sha256"],
            "evidence_root_id": bracket_binding["evidence_root_id"],
            "runs_root": bracket_binding["runs_root"],
        }
        bound_session_id = str(bracket_binding["session_id"])
        for candidate in candidates:
            if candidate.bracket_session_id != bound_session_id:
                continue
            if (
                candidate.bracket_window_id,
                candidate.bracket_plan_id,
                candidate.bracket_plan_sha256,
                candidate.bracket_evidence_root_id,
                candidate.bracket_runs_root,
            ) != (
                bracket_window_id,
                bracket_plan_id,
                bracket_plan_sha256,
                bracket_evidence_root_id,
                expected_runs_root,
            ):
                return result, ("calibration_bracket_binding_invalid",)
    # v2 remains an authenticated validation/reduction artifact, but only the
    # 59-pulse v3 protocol carries the governed 95/95 claim calibration.
    matching = [
        candidate
        for candidate in candidates
        if candidate.protocol_id == PROTOCOL_ID
        and all(
            candidate.bindings.get(field) == bindings.get(field)
            for field in V2_BINDING_FIELDS
        )
    ]
    matching_decimals: dict[int, Decimal] = {}
    for candidate in matching:
        candidate_decimal = _candidate_decimal(candidate)
        if candidate_decimal is None or candidate_decimal < 0:
            return result, ("instrument_calibration_invalid",)
        matching_decimals[id(candidate)] = candidate_decimal
    corpus_members = artifact["derivation_corpus"]["members"]
    observed_triggers = result["acceptance"]["prospective_rederivation"][
        "observed_triggers"
    ]
    if (
        protocol_sha256(PROTOCOL_ID) != prospective.get("protocol_sha256")
        or _current_estimator_code_sha256()
        != dict(prospective["estimator_code_sha256"])
    ):
        observed_triggers.append("protocol_or_estimator_byte_change")
    prior_ids = {
        observation["content_id"]
        for observation in artifact["prior_observation_set"]["observations"]
    }
    distinct_observations = {
        observation.content_id: observation
        for observation in ledger_snapshot.observations
        if observation.content_id is not None
    }
    distinct_live_observations = {
        content_id: observation
        for content_id, observation in distinct_observations.items()
        if not observation.is_historical_import
    }
    new_observations = [
        observation
        for content_id, observation in sorted(distinct_live_observations.items())
        if content_id not in prior_ids
    ]
    new_observations.extend(
        sorted(
            (
                observation
                for observation in ledger_snapshot.post_cutoff_live_observations(
                    cutoff["sequence"]
                )
                if observation.content_id is None
            ),
            key=lambda observation: (observation.sequence, observation.attempt_id),
        )
    )
    if any(
        observation.classification_disposition
        not in {"valid", "systematic-invalid", "ordinary-invalid"}
        for observation in new_observations
    ):
        return result, ("calibration_observation_unclassifiable",)
    valid_same_epoch = [
        observation
        for observation in distinct_observations.values()
        if observation.disposition == "valid"
        and dict(observation.identity_epoch) == dict(identity_epoch)
    ]
    if len(valid_same_epoch) >= 38:
        observed_triggers.append("corpus_doubles_from_19_to_38")
    corpus_values = [
        Decimal(member["b_fiducial_s"]) for member in corpus_members
    ]
    new_valid_values = [
        value
        for observation in new_observations
        if observation.disposition == "valid"
        and dict(observation.identity_epoch) == dict(identity_epoch)
        and (value := _decimal(observation.exact_bound_lexeme_s)) is not None
    ]
    if any(value < min(corpus_values) or value > max(corpus_values) for value in new_valid_values):
        observed_triggers.append(
            "new_valid_same_identity_capture_expands_observed_range"
        )
    if any(
        observation.disposition == "systematic-invalid"
        and dict(observation.identity_epoch) == dict(identity_epoch)
        for observation in new_observations
    ):
        observed_triggers.append(
            "new_systematic_failure_challenges_preflight_screen"
        )
    # R2 trigger evaluation ranges over the observation universe, not the
    # narrower bracket-candidate set.  A governed aborted PRE can therefore
    # stale the acceptance artifact even when no eligible endpoint pair is
    # available for this window.
    observation_stale_triggers = [
        trigger
        for trigger in observed_triggers
        if trigger == "new_systematic_failure_challenges_preflight_screen"
    ]
    if observation_stale_triggers:
        result["acceptance"]["freshness"].update(
            {
                "status": "stale",
                "reason": "prospective_rederivation_required",
                "stale_triggers": observation_stale_triggers,
            }
        )
        return result, ("calibration_acceptance_bound_stale",)
    causal_pre = [
        candidate for candidate in matching if candidate.capture_wall_time_s <= window_start_s
    ]
    causal_post = [
        candidate for candidate in matching if candidate.capture_wall_time_s >= window_end_s
    ]
    fresh_pre = [
        candidate
        for candidate in causal_pre
        if window_end_s <= candidate.capture_wall_time_s + MAX_AGE_S
    ]
    fresh_post = [
        candidate
        for candidate in causal_post
        if candidate.capture_wall_time_s - window_start_s <= MAX_AGE_S
    ]
    if not fresh_pre or not fresh_post:
        reason = (
            "instrument_calibration_stale"
            if (causal_pre and not fresh_pre) or (causal_post and not fresh_post)
            else "instrument_calibration_bracket_missing"
        )
        return result, (reason,)
    if bound_observations is None:
        pre = max(fresh_pre, key=lambda candidate: candidate.capture_wall_time_s)
        post = min(fresh_post, key=lambda candidate: candidate.capture_wall_time_s)
    else:
        candidate_by_receipt = {
            candidate.ledger_receipt_digest: candidate for candidate in matching
        }
        pre = candidate_by_receipt.get(bound_observations[0].receipt_digest)
        post = candidate_by_receipt.get(bound_observations[1].receipt_digest)
        if pre not in fresh_pre or post not in fresh_post:
            return result, ("calibration_bracket_binding_invalid",)
    pre_decimal = matching_decimals[id(pre)]
    post_decimal = matching_decimals[id(post)]
    if (
        not pre_decimal.is_finite()
        or not post_decimal.is_finite()
        or pre_decimal < 0
        or post_decimal < 0
    ):
        return result, ("instrument_calibration_invalid",)
    if isinstance(pre.b_fiducial_s, float) and isinstance(
        post.b_fiducial_s, float
    ):
        # Old synthetic probes supplied only binary64 endpoints. Preserve their
        # source arithmetic without applying Decimal after a second rounding;
        # authenticated production candidates always use the exact branch.
        drift_decimal = Decimal(
            str(abs(pre.b_fiducial_s - post.b_fiducial_s))
        )
    else:
        drift_decimal = abs(pre_decimal - post_decimal)
    endpoint_max_decimal = max(pre_decimal, post_decimal)
    operatives = artifact["decimal_derivation"]["ratified_operatives"]
    screen = Decimal(operatives["bracket_screen_s"])
    preflight_screen = Decimal(operatives["preflight_level_screen_s"])
    maximum_drift = Decimal(operatives["maximum_budgetable_drift_s"])
    maximum_excess = Decimal(operatives["max_budgetable_excess_s"])
    result.update(
        {
            "pre": pre.descriptor(),
            "post": post.descriptor(),
            "endpoint_max_b_fiducial_s": float(endpoint_max_decimal),
            "drift_s": float(drift_decimal),
        }
    )
    result["acceptance"]["numeric_semantics"].update(
        {
            "pre_b_fiducial_binary64_s": float(pre_decimal),
            "pre_b_fiducial_decimal_s": str(pre_decimal),
        "endpoint_max_b_fiducial_s": str(endpoint_max_decimal),
        "operative_b_fiducial_decimal_s": str(operative_bound),
        "operative_b_fiducial_binary64_s": float(operative_bound),
    }
    result["status"] = "passed"
    return result, ()


def calibration_bracket_for_bundles(
    runs_root: Path,
    bundle_paths: Sequence[Path],
    policy: CalibrationBracketingPolicy,
    *,
    ledger_snapshot: CalibrationLedgerSnapshot | None = None,
    bracket_binding: Mapping[str, Any] | None = None,
    bracket_window_id: str | None = None,
    bracket_plan_id: str | None = None,
    bracket_plan_sha256: str | None = None,
    bracket_evidence_root_id: str | None = None,
    _allow_unissued_fixture: bool = False,
) -> tuple[dict[str, Any], tuple[str, ...]]:
    """Use the runs root only for the evaluated window's T1/endpoints."""

    if not bundle_paths:
        empty, _ = evaluate_calibration_bracket(
            (),
            window_start_s=0.0,
            window_end_s=0.0,
            bindings={},
            policy=policy,
            ledger_snapshot=ledger_snapshot,
            _allow_unissued_fixture=_allow_unissued_fixture,
        )
        return empty, ("instrument_calibration_bracket_missing",)
    windows = []
    bindings: list[Mapping[str, Any]] = []
    try:
        for path in bundle_paths:
            reader = BundleReader(path)
            window = reader.measured_window()
            metadata = reader.metadata()
            calibration = metadata.get("instrument_calibration")
            binding = calibration.get("bindings") if isinstance(calibration, Mapping) else None
            if window is None or not isinstance(binding, Mapping):
                raise ValueError("member omits calibration binding evidence")
            windows.append(window)
            bindings.append(binding)
    except (BundleReadError, OSError, TypeError, ValueError):
        empty, _ = evaluate_calibration_bracket(
            (),
            window_start_s=0.0,
            window_end_s=0.0,
            bindings={},
            policy=policy,
            ledger_snapshot=ledger_snapshot,
            _allow_unissued_fixture=_allow_unissued_fixture,
        )
        return empty, ("instrument_calibration_bracket_missing",)
    expected = bindings[0]
    if any(
        any(binding.get(field) != expected.get(field) for field in V2_BINDING_FIELDS)
        for binding in bindings[1:]
    ):
        empty, _ = evaluate_calibration_bracket(
            (),
            window_start_s=min(window.start_s for window in windows),
            window_end_s=max(window.end_s for window in windows),
            bindings=expected,
            policy=policy,
            ledger_snapshot=ledger_snapshot,
            _allow_unissued_fixture=_allow_unissued_fixture,
        )
        return empty, ("instrument_calibration_mismatch",)
    if ledger_snapshot is None:
        candidates: tuple[CalibrationCandidate, ...] = ()
    else:
        candidates = discover_calibration_candidates(ledger_snapshot)
        registered_valid = sum(
            observation.disposition == "valid"
            and not observation.is_historical_import
            and (
                observation.bracket_session_id is None
                or any(
                    session.session_id == observation.bracket_session_id
                    and session.state == "finalized"
                    for session in ledger_snapshot.bracket_sessions
                )
            )
            for observation in ledger_snapshot.observations
        )
        if ledger_snapshot.valid and len(candidates) != registered_valid:
            empty, _ = evaluate_calibration_bracket(
                (),
                window_start_s=min(window.start_s for window in windows),
                window_end_s=max(window.end_s for window in windows),
                bindings=expected,
                policy=policy,
                ledger_snapshot=ledger_snapshot,
                _allow_unissued_fixture=_allow_unissued_fixture,
            )
            return empty, ("calibration_ledger_custody_invalid",)
    return evaluate_calibration_bracket(
        candidates,
        window_start_s=min(window.start_s for window in windows),
        window_end_s=max(window.end_s for window in windows),
        bindings=expected,
        policy=policy,
        ledger_snapshot=ledger_snapshot,
        bracket_binding=bracket_binding,
        bracket_window_id=bracket_window_id,
        bracket_plan_id=bracket_plan_id,
        bracket_plan_sha256=bracket_plan_sha256,
        bracket_evidence_root_id=bracket_evidence_root_id,
        bracket_runs_root=runs_root,
        _allow_unissued_fixture=_allow_unissued_fixture,
    )


__all__ = [
    "ACCEPTANCE_BOUND_SCHEMA",
    "ACCEPTANCE_EVALUATION_SCHEMA",
    "BRACKET_BINDING_SCHEMA",
    "BRACKET_SCHEMA",
    "CalibrationCandidate",
    "build_calibration_bracket_binding",
    "calibration_bracket_for_bundles",
    "discover_calibration_candidates",
    "evaluate_calibration_bracket",
    "load_calibration_acceptance_bound",
    "load_calibration_candidate",
    "validate_calibration_bracket_binding",
]

exec
/bin/zsh -lc "git show impl/d117-u1-ledger-session:joulewise/calibration_ledger.py | rg -n '"'^def (append_bracket_session_receipt|claim_bracket_session_slot|finalize_bracket_session_slot|abort_bracket_session|load_calibration_ledger_snapshot|write_calibration_ledger_head_pin)|''^def .*head'"'; git show impl/d117-u1-ledger-session:joulewise/calibration_bracketing.py | rg -n '"'^def (build_calibration_bracket_binding|validate_calibration_bracket_binding|discover_calibration_candidates|evaluate_calibration_bracket|calibration_bracket_for_bundles)'"'" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
740:def _head_pin(value: object) -> tuple[int, str] | None:
1233:def load_calibration_ledger_snapshot(
2430:def _authenticated_head_pin(
2509:def append_bracket_session_receipt(
2585:def claim_bracket_session_slot(
2650:def finalize_bracket_session_slot(
2729:def abort_bracket_session(
2778:def terminal_head_pin_for_session(
2955:def _head_pin_for_valid_receipt(receipt: Mapping[str, Any]) -> dict[str, Any]:
2965:def head_pin_for_receipt(receipt: Mapping[str, Any]) -> dict[str, Any]:
536:def build_calibration_bracket_binding(
612:def validate_calibration_bracket_binding(
929:def discover_calibration_candidates(
1015:def evaluate_calibration_bracket(
1598:def calibration_bracket_for_bundles(

exec
/bin/zsh -lc "git show impl/d117-u1-ledger-session:joulewise/calibration_ledger.py | sed -n '1215,1325p;2490,2825p;2940,2990p'; git show impl/d117-u1-ledger-session:joulewise/calibration_bracketing.py | sed -n '520,735p;920,980p'" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
        if not observation.artifact_sha256:
            if observation.disposition == "abandoned":
                continue
            return {"calibration_ledger_custody_invalid"}
        root = Path(observation.custody_locator)
        if not root.is_absolute():
            root = Path(repo_root) / root
        for relative, expected in observation.artifact_sha256.items():
            path = root / relative
            try:
                actual = hashlib.sha256(path.read_bytes()).hexdigest()
            except OSError:
                return {"calibration_ledger_custody_invalid"}
            if actual != expected:
                return {"calibration_ledger_custody_invalid"}
    return set()


def load_calibration_ledger_snapshot(
    ledger_path: Path = DEFAULT_LEDGER_PATH,
    head_pin_path: Path = DEFAULT_HEAD_PIN_PATH,
    *,
    baseline_sequence: int | None = None,
    baseline_digest: str | None = None,
    require_committed_pin: bool = True,
    verify_custody: bool = True,
    repo_root: Path = REPO_ROOT,
) -> CalibrationLedgerSnapshot:
    """Load, authenticate, and freeze exactly one ledger snapshot.

    A proper physical prefix of the pin is classified explicitly as rollback;
    any other physical/pinned disagreement is a stale-head mismatch.  The
    baseline must occur at its exact sequence in the same complete chain.
    This closes workflow omission, unregistered evidence, and rollback or
    stale-head consumption; it does not defend against a malicious trusted
    writer or a rewrite of both Git and the full ledger history.
    """

    ledger_path = Path(ledger_path)
    head_pin_path = Path(head_pin_path)
    reasons: set[str] = set()
    try:
        pin_raw = head_pin_path.read_bytes()
        pin_value = json.loads(pin_raw)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        pin_raw = b""
        pin_value = None
    pin = _head_pin(pin_value)
    if pin is None:
        reasons.add("calibration_ledger_malformed")
        pinned_sequence, pinned_digest = 0, GENESIS_DIGEST
    else:
        pinned_sequence, pinned_digest = pin
    try:
        raw = ledger_path.read_bytes()
    except OSError:
        raw = b""
        if pinned_sequence > 0:
            reasons.add("calibration_ledger_missing")
    genesis_development_bootstrap = (
        pinned_sequence == 0
        and pinned_digest == GENESIS_DIGEST
        and not raw
        and not ledger_path.exists()
    )
    if (
        require_committed_pin
        # The checked-in fixture starts at genesis.  Before its first commit,
        # an absent physical ledger cannot license a claim (there are no
        # endpoints); permitting this development-only empty view avoids a
        # circular "commit before tests" bootstrap. Any physical byte or any
        # non-genesis pin remains strictly commit-authenticated.
        and not genesis_development_bootstrap
        and _committed_pin_bytes(head_pin_path, repo_root) != pin_raw
    ):
        reasons.add("calibration_ledger_head_uncommitted")
    append_journal, malformed_journal = _read_append_journal(ledger_path)
    receipts, parse_reasons = _parse_ledger(
        raw,
        append_journal=append_journal,
    )
    if malformed_journal:
        parse_reasons.add("calibration_ledger_malformed")
    reasons.update(parse_reasons)
    physical_sequence = len(receipts)
    physical_digest = (
        str(receipts[-1]["receipt_digest"]) if receipts else GENESIS_DIGEST
    )
    if (physical_sequence, physical_digest) != (pinned_sequence, pinned_digest):
        if physical_sequence < pinned_sequence:
            reasons.add("calibration_ledger_rollback")
        else:
            reasons.add("calibration_ledger_head_mismatch")
    if baseline_sequence is not None or baseline_digest is not None:
        if (
            isinstance(baseline_sequence, bool)
            or not isinstance(baseline_sequence, int)
            or baseline_sequence < 0
            or not _is_sha256(baseline_digest)
        ):
            reasons.add("calibration_ledger_baseline_missing")
        else:
            in_chain = (
                baseline_digest == GENESIS_DIGEST
                if baseline_sequence == 0
                else baseline_sequence <= len(receipts)
                and receipts[baseline_sequence - 1]["receipt_digest"]
                == baseline_digest
            )
            if not in_chain or baseline_sequence > pinned_sequence:
                reasons.add("calibration_ledger_baseline_missing")
        normalized_slots[role] = {
            "attempt_id": source.get("attempt_id"),
            "custody_locator": str(custody),
            "identity_epoch": _normalized_vector(
                source.get("identity_epoch"), IDENTITY_EPOCH_FIELDS
            ),
            "t1_bindings": _normalized_vector(source.get("t1_bindings"), T1_FIELDS),
            "expected_time_role": role,
        }
    if not _valid_session_identity(session_identity) or any(
        not _valid_session_slot_reservation(normalized_slots[role], role)
        for role in BRACKET_SESSION_SLOTS
    ):
        raise CalibrationLedgerError("bracket session reservation is malformed")
    if normalized_slots["pre"]["attempt_id"] == normalized_slots["post"]["attempt_id"]:
        raise CalibrationLedgerError("bracket session slot attempts must be distinct")
    return _frozen_mapping(session_identity), _frozen_mapping(normalized_slots)


def append_bracket_session_receipt(
    ledger_path: Path,
    *,
    session_id: str,
    window_id: str,
    plan_id: str,
    plan_sha256: str,
    evidence_root_id: str,
    runs_root: Path | str,
    slots: Mapping[str, Mapping[str, Any]],
    head_pin_path: Path = DEFAULT_HEAD_PIN_PATH,
    require_committed_pin: bool = True,
    repo_root: Path = REPO_ROOT,
) -> Mapping[str, Any]:
    """Atomically reserve exactly one immutable pre/post bracket capability.

    Physical-head equality with the committed pin is checked here, at open,
    and deliberately not checked again while either already-reserved slot is
    finalized. Claim evaluation remains impossible until the terminal head
    pin is emitted, reviewed, and committed.
    """

    session_identity, normalized_slots = validate_bracket_session_reservation_inputs(
        session_id=session_id,
        window_id=window_id,
        plan_id=plan_id,
        plan_sha256=plan_sha256,
        evidence_root_id=evidence_root_id,
        runs_root=runs_root,
        slots=slots,
    )
    pin = _authenticated_head_pin(
        Path(head_pin_path),
        require_committed_pin=require_committed_pin,
        repo_root=Path(repo_root),
    )

    def build(receipts: Sequence[Mapping[str, Any]]) -> Mapping[str, Any]:
        predecessor = receipts[-1]["receipt_digest"] if receipts else GENESIS_DIGEST
        if (len(receipts), predecessor) != pin:
            raise CalibrationLedgerError(
                "physical ledger head differs from the committed pin"
            )
        observations, sessions, reasons = _attempts_and_observations(receipts)
        del observations
        if reasons:
            raise CalibrationLedgerError(", ".join(sorted(reasons)))
        reserved_attempts = {
            attempt_id
            for session in sessions
            for attempt_id in session.slot_attempt_ids.values()
        }
        ordinary_attempts = {
            str(receipt["attempt_id"])
            for receipt in receipts
            if receipt.get("schema_version") == RECEIPT_SCHEMA
        }
        proposed_attempts = {
            normalized_slots[role]["attempt_id"] for role in BRACKET_SESSION_SLOTS
        }
        if (
            any(session.session_id == session_id for session in sessions)
            or proposed_attempts & (reserved_attempts | ordinary_attempts)
        ):
            raise CalibrationLedgerError("bracket session identity conflicts with ledger")
        return _new_bracket_session_record(
            sequence=len(receipts) + 1,
            predecessor_digest=str(predecessor),
            event=BRACKET_SESSION_OPEN_EVENT,
            session_identity=session_identity,
            fields={"slots": normalized_slots},
        )

    return _locked_append(Path(ledger_path), build)


def claim_bracket_session_slot(
    ledger_path: Path,
    *,
    session_id: str,
    slot: str,
    attempt_id: str,
    claim_id: str,
) -> Mapping[str, Any]:
    """Append one process-death-stable exclusive claim for a reserved slot."""

    if slot not in BRACKET_SESSION_SLOTS:
        raise CalibrationLedgerError(f"invalid bracket session slot: {slot!r}")
    if not isinstance(claim_id, str) or not claim_id:
        raise CalibrationLedgerError("bracket slot claim_id must be nonempty")

    def build(receipts: Sequence[Mapping[str, Any]]) -> Mapping[str, Any]:
        observations, sessions, reasons = _attempts_and_observations(receipts)
        del observations
        non_open_reasons = reasons - {"calibration_ledger_bracket_session_open"}
        if non_open_reasons:
            raise CalibrationLedgerError(", ".join(sorted(non_open_reasons)))
        session = next(
            (item for item in sessions if item.session_id == session_id), None
        )
        if session is None or session.state != "open":
            raise CalibrationLedgerError("bracket session is not open")
        expected_slot = BRACKET_SESSION_SLOTS[len(session.finalized_slots)]
        if slot != expected_slot or session.slot_attempt_ids.get(slot) != attempt_id:
            raise CalibrationLedgerError(
                f"bracket session slot must claim in order: expected {expected_slot}"
            )
        existing = [
            receipt
            for receipt in receipts
            if receipt.get("schema_version") == BRACKET_SESSION_SCHEMA
            and receipt.get("event") == BRACKET_SESSION_SLOT_CLAIM_EVENT
            and receipt.get("session_id") == session_id
            and receipt.get("slot") == slot
        ]
        if existing:
            raise CalibrationLedgerError("calibration_ledger_bracket_slot_claimed")
        open_receipt = next(
            receipt
            for receipt in receipts
            if receipt.get("event") == BRACKET_SESSION_OPEN_EVENT
            and receipt.get("session_id") == session_id
        )
        predecessor = receipts[-1]["receipt_digest"] if receipts else GENESIS_DIGEST
        return _new_bracket_session_record(
            sequence=len(receipts) + 1,
            predecessor_digest=str(predecessor),
            event=BRACKET_SESSION_SLOT_CLAIM_EVENT,
            session_identity={
                field: open_receipt[field] for field in _SESSION_IDENTITY_KEYS
            },
            fields={
                "slot": slot,
                "attempt_id": attempt_id,
                "claim_id": claim_id,
            },
        )

    return _locked_append(Path(ledger_path), build)


def finalize_bracket_session_slot(
    ledger_path: Path,
    *,
    session_id: str,
    slot: str,
    disposition: str,
    custody_locator: str,
    artifact_sha256: Mapping[str, str] | None = None,
    identity_epoch: Mapping[str, Any] | None = None,
    t1_bindings: Mapping[str, Any] | None = None,
    capture_wall_time_s: str | None = None,
    exact_bound_lexeme_s: str | None = None,
) -> Mapping[str, Any]:
    """Fill exactly one reserved session slot in mandatory pre/post order."""

    if slot not in BRACKET_SESSION_SLOTS:
        raise CalibrationLedgerError(f"invalid bracket session slot: {slot!r}")
    if disposition not in FINAL_DISPOSITIONS:
        raise CalibrationLedgerError(f"invalid final disposition: {disposition!r}")
    artifacts = dict(artifact_sha256 or {})
    content_id = content_id_from_artifact_hashes(artifacts)
    normalized_epoch = _normalized_vector(identity_epoch, IDENTITY_EPOCH_FIELDS)
    normalized_t1 = _normalized_vector(t1_bindings, T1_FIELDS)

    def build(receipts: Sequence[Mapping[str, Any]]) -> Mapping[str, Any]:
        observations, sessions, reasons = _attempts_and_observations(receipts)
        del observations
        non_open_reasons = reasons - {"calibration_ledger_bracket_session_open"}
        if non_open_reasons:
            raise CalibrationLedgerError(", ".join(sorted(non_open_reasons)))
        by_id = {session.session_id: session for session in sessions}
        session = by_id.get(session_id)
        if session is None or session.state != "open":
            raise CalibrationLedgerError("bracket session is not open")
        expected_slot = BRACKET_SESSION_SLOTS[len(session.finalized_slots)]
        if slot != expected_slot or slot in session.finalized_slots:
            raise CalibrationLedgerError(
                f"bracket session slot must finalize in order: expected {expected_slot}"
            )
        open_receipt = next(
            receipt
            for receipt in receipts
            if receipt.get("event") == BRACKET_SESSION_OPEN_EVENT
            and receipt.get("session_id") == session_id
        )
        reserved = open_receipt["slots"][slot]
        if (
            reserved["custody_locator"] != custody_locator
            or dict(reserved["identity_epoch"]) != normalized_epoch
            or dict(reserved["t1_bindings"]) != normalized_t1
        ):
            raise CalibrationLedgerError(
                "slot finalization conflicts with the reserved session binding"
            )
        predecessor = receipts[-1]["receipt_digest"] if receipts else GENESIS_DIGEST
        return _new_bracket_session_record(
            sequence=len(receipts) + 1,
            predecessor_digest=str(predecessor),
            event=BRACKET_SESSION_FINALIZATION_EVENT,
            session_identity={
                field: open_receipt[field] for field in _SESSION_IDENTITY_KEYS
            },
            fields={
                "slot": slot,
                "attempt_id": reserved["attempt_id"],
                "content_id": content_id,
                "artifact_sha256": dict(sorted(artifacts.items())),
                "identity_epoch": normalized_epoch,
                "t1_bindings": normalized_t1,
                "capture_wall_time_s": capture_wall_time_s,
                "exact_bound_lexeme_s": exact_bound_lexeme_s,
                "disposition": disposition,
                "custody_locator": custody_locator,
            },
        )

    return _locked_append(Path(ledger_path), build)


def abort_bracket_session(
    ledger_path: Path,
    *,
    session_id: str,
    reason: str,
) -> Mapping[str, Any]:
    """Append a governed terminal closure without deleting partial receipts."""

    if not isinstance(reason, str) or not reason:
        raise CalibrationLedgerError("bracket session abort reason must be nonempty")

    def build(receipts: Sequence[Mapping[str, Any]]) -> Mapping[str, Any]:
        observations, sessions, reasons = _attempts_and_observations(receipts)
        del observations
        non_open_reasons = reasons - {"calibration_ledger_bracket_session_open"}
        if non_open_reasons:
            raise CalibrationLedgerError(", ".join(sorted(non_open_reasons)))
        session = next(
            (item for item in sessions if item.session_id == session_id), None
        )
        if session is None or session.state != "open":
            raise CalibrationLedgerError("bracket session is not open")
        open_receipt = next(
            receipt
            for receipt in receipts
            if receipt.get("event") == BRACKET_SESSION_OPEN_EVENT
            and receipt.get("session_id") == session_id
        )
        predecessor = receipts[-1]["receipt_digest"] if receipts else GENESIS_DIGEST
        finalized_slots = list(session.finalized_slots)
        return _new_bracket_session_record(
            sequence=len(receipts) + 1,
            predecessor_digest=str(predecessor),
            event=BRACKET_SESSION_ABORT_EVENT,
            session_identity={
                field: open_receipt[field] for field in _SESSION_IDENTITY_KEYS
            },
            fields={
                "finalized_slots": finalized_slots,
                "unused_slots": [
                    role for role in BRACKET_SESSION_SLOTS if role not in finalized_slots
                ],
                "reason": reason,
            },
        )

    return _locked_append(Path(ledger_path), build)


def terminal_head_pin_for_session(
    ledger_path: Path,
    *,
    session_id: str,
) -> dict[str, Any]:
    """Return the sole terminal pin candidate after post or governed abort."""

    try:
        raw = Path(ledger_path).read_bytes()
    except OSError as exc:
        raise CalibrationLedgerError("ledger is unreadable") from exc
    receipts, parse_reasons = _parse_ledger(raw)
    observations, sessions, state_reasons = _attempts_and_observations(receipts)
    del observations
    reasons = parse_reasons | state_reasons
    if reasons:
        raise CalibrationLedgerError(", ".join(sorted(reasons)))
    session = next((item for item in sessions if item.session_id == session_id), None)
    if session is None or session.state == "open":
        raise CalibrationLedgerError("bracket session is not terminal")
    terminal_digest = (
        session.finalized_slots["post"].receipt_digest
        if session.state == "finalized"
        else session.abort_receipt_digest
    )
    final = receipts[-1] if receipts else None
    if final is None or final["receipt_digest"] != terminal_digest:
        raise CalibrationLedgerError("session closure is not the terminal ledger head")
    return _head_pin_for_valid_receipt(final)


def append_pending_receipt(
    ledger_path: Path,
    *,
    attempt_id: str,
    custody_locator: str,
    identity_epoch: Mapping[str, Any] | None = None,
    t1_bindings: Mapping[str, Any] | None = None,
    head_pin_path: Path = DEFAULT_HEAD_PIN_PATH,
    require_committed_pin: bool = True,
    repo_root: Path = REPO_ROOT,
) -> Mapping[str, Any]:
    """Reserve an attempt before any capture directory or sampler exists.

    This closes workflow omission, unregistered evidence, and rollback or
    stale-head consumption; it does not defend against a malicious trusted
    writer or a rewrite of both Git and the full ledger history.
    """
            event="finalization",
            attempt_id=attempt_id,
            content_id=content_id,
            artifacts=artifacts,
            identity_epoch=identity_epoch,
            t1_bindings=t1_bindings,
            capture_wall_time_s=capture_wall_time_s,
            exact_bound_lexeme_s=exact_bound_lexeme_s,
            disposition=disposition,
            custody_locator=custody_locator,
        )

    return _locked_append(Path(ledger_path), build)


def _head_pin_for_valid_receipt(receipt: Mapping[str, Any]) -> dict[str, Any]:
    if not _valid_receipt_shape(receipt):
        raise CalibrationLedgerError("cannot pin a malformed receipt")
    return {
        "sequence": int(receipt["sequence"]),
        "head_digest": str(receipt["receipt_digest"]),
        "ledger_schema": LEDGER_SCHEMA,
    }


def head_pin_for_receipt(receipt: Mapping[str, Any]) -> dict[str, Any]:
    """Emit a pin for an ordinary receipt, never a mid-session receipt."""

    if receipt.get("schema_version") == BRACKET_SESSION_SCHEMA:
        raise CalibrationLedgerError(
            "bracket session receipts require terminal_head_pin_for_session"
        )
    return _head_pin_for_valid_receipt(receipt)


__all__ = [
    "ALL_DISPOSITIONS",
    "BRACKET_SESSION_ABORT_EVENT",
    "BRACKET_SESSION_FINALIZATION_EVENT",
    "BRACKET_SESSION_OPEN_EVENT",
    "BRACKET_SESSION_SLOT_CLAIM_EVENT",
    "BRACKET_SESSION_SCHEMA",
    "BRACKET_SESSION_SLOTS",
    "CONTENT_ID_ARTIFACTS",
    "DEFAULT_HEAD_PIN_PATH",
    "DEFAULT_LEDGER_PATH",
    "FINAL_DISPOSITIONS",
    "GENESIS_DIGEST",
    "GOVERNED_ARTIFACTS",
    "HISTORICAL_IMPORT_EVENT_PREFIX",
    "HISTORICAL_IMPORT_CUSTODY_MANIFEST_SCHEMA",
    "capability_receipt_digest",
    "terminal_head",
    "endpoints",
    "binding_digest",
}
_BRACKET_ENDPOINT_KEYS = {
    "attempt_id",
    "receipt_digest",
    "content_digest",
}


def _binding_core(binding: Mapping[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in binding.items() if key != "binding_digest"}


def build_calibration_bracket_binding(
    ledger_snapshot: CalibrationLedgerSnapshot,
    *,
    session_id: str,
    window_id: str,
    plan_id: str,
    plan_sha256: str,
    evidence_root_id: str,
    runs_root: Path | str,
) -> dict[str, Any]:
    """Bind one frozen window to its exact finalized session endpoints."""

    if not isinstance(ledger_snapshot, CalibrationLedgerSnapshot) or not ledger_snapshot.valid:
        raise ValueError("bracket binding requires a valid pinned ledger snapshot")
    session = ledger_snapshot.bracket_session_by_id.get(session_id)
    expected_identity = (
        window_id,
        plan_id,
        plan_sha256,
        evidence_root_id,
        str(Path(runs_root).absolute()),
    )
    if (
        session is None
        or session.state != "finalized"
        or (
            session.window_id,
            session.plan_id,
            session.plan_sha256,
            session.evidence_root_id,
            session.runs_root,
        )
        != expected_identity
    ):
        raise ValueError("bracket session does not match the frozen window identity")
    pre = session.finalized_slots.get("pre")
    post = session.finalized_slots.get("post")
    if (
        pre is None
        or post is None
        or pre.disposition != "valid"
        or post.disposition != "valid"
        or pre.content_id is None
        or post.content_id is None
        or post.sequence != ledger_snapshot.head_sequence
        or post.receipt_digest != ledger_snapshot.head_digest
    ):
        raise ValueError("bracket session endpoints are not valid at the terminal head")
    binding: dict[str, Any] = {
        "schema_version": BRACKET_BINDING_SCHEMA,
        "ledger_schema": LEDGER_SCHEMA,
        "session_id": session.session_id,
        "window_id": session.window_id,
        "plan_id": session.plan_id,
        "plan_sha256": session.plan_sha256,
        "evidence_root_id": session.evidence_root_id,
        "runs_root": session.runs_root,
        "capability_receipt_digest": session.capability_receipt_digest,
        "terminal_head": {
            "sequence": post.sequence,
            "head_digest": post.receipt_digest,
            "ledger_schema": LEDGER_SCHEMA,
        },
        "endpoints": {
            role: {
                "attempt_id": observation.attempt_id,
                "receipt_digest": observation.receipt_digest,
                "content_digest": observation.content_id,
            }
            for role, observation in (("pre", pre), ("post", post))
        },
    }
    binding["binding_digest"] = _canonical_sha256(binding)
    return binding


def validate_calibration_bracket_binding(
    binding: Mapping[str, Any],
    ledger_snapshot: CalibrationLedgerSnapshot,
    *,
    window_id: str | None = None,
    plan_id: str | None = None,
    plan_sha256: str | None = None,
    evidence_root_id: str | None = None,
    runs_root: Path | str | None = None,
) -> tuple[LedgerObservation, LedgerObservation] | None:
    """Return the exact authenticated pair, or ``None`` on any substitution."""

    if (
        not isinstance(binding, Mapping)
        or set(binding) != _BRACKET_BINDING_KEYS
        or binding.get("schema_version") != BRACKET_BINDING_SCHEMA
        or binding.get("ledger_schema") != LEDGER_SCHEMA
        or not _valid_sha256(binding.get("plan_sha256"))
        or not _valid_sha256(binding.get("capability_receipt_digest"))
        or not _valid_sha256(binding.get("binding_digest"))
        or binding.get("binding_digest") != _canonical_sha256(_binding_core(binding))
        or not isinstance(ledger_snapshot, CalibrationLedgerSnapshot)
        or not ledger_snapshot.valid
    ):
        return None
    if any(
        not isinstance(value, str) or not value
        for value in (window_id, plan_id, plan_sha256, evidence_root_id)
    ) or runs_root is None:
        return None
    expected_runs_root = str(Path(runs_root).absolute())
    for field, expected in (
        ("window_id", window_id),
        ("plan_id", plan_id),
        ("plan_sha256", plan_sha256),
        ("evidence_root_id", evidence_root_id),
        ("runs_root", expected_runs_root),
    ):
        if binding.get(field) != expected:
            return None
    session = ledger_snapshot.bracket_session_by_id.get(str(binding.get("session_id")))
    if (
        session is None
        or session.state != "finalized"
        or binding.get("window_id") != session.window_id
        or binding.get("plan_id") != session.plan_id
        or binding.get("plan_sha256") != session.plan_sha256
        or binding.get("evidence_root_id") != session.evidence_root_id
        or binding.get("runs_root") != session.runs_root
        or binding.get("capability_receipt_digest")
        != session.capability_receipt_digest
    ):
        return None
    terminal = binding.get("terminal_head")
    endpoints = binding.get("endpoints")
    if (
        not isinstance(terminal, Mapping)
        or set(terminal) != {"sequence", "head_digest", "ledger_schema"}
        or terminal.get("ledger_schema") != LEDGER_SCHEMA
        or isinstance(terminal.get("sequence"), bool)
        or not isinstance(terminal.get("sequence"), int)
        or not _valid_sha256(terminal.get("head_digest"))
        or not isinstance(endpoints, Mapping)
        or set(endpoints) != {"pre", "post"}
    ):
        return None
    resolved: list[LedgerObservation] = []
    for role in ("pre", "post"):
        endpoint = endpoints.get(role)
        observation = session.finalized_slots.get(role)
        if (
            not isinstance(endpoint, Mapping)
            or set(endpoint) != _BRACKET_ENDPOINT_KEYS
            or observation is None
            or observation.disposition != "valid"
            or observation.content_id is None
            or endpoint.get("attempt_id") != observation.attempt_id
            or endpoint.get("receipt_digest") != observation.receipt_digest
            or endpoint.get("content_digest") != observation.content_id
        ):
            return None
        resolved.append(observation)
    post = resolved[1]
    if (
        terminal.get("sequence") != post.sequence
        or terminal.get("head_digest") != post.receipt_digest
        or post.sequence > len(ledger_snapshot.receipts)
        or ledger_snapshot.receipts[post.sequence - 1].get("receipt_digest")
        != post.receipt_digest
    ):
        return None
    return resolved[0], resolved[1]


def _binding_evidence_authentic(
    evidence: Mapping[str, Any], bindings: Mapping[str, Any]
) -> bool:
    binding_evidence = evidence.get("binding_evidence")
    binary = (
        binding_evidence.get("powermetrics_binary")
        if isinstance(binding_evidence, Mapping)
        else None
    )
    power_policy = (
        binding_evidence.get("power_policy")
        if isinstance(binding_evidence, Mapping)
        else None
    )
    # Canonical form MUST match the generation (powermetrics_fiducial) and
    # reduce-side consumers byte-for-byte: ensure_ascii=False (delta-review
    # P2 — the ASCII-default form made authentic non-ASCII binding vectors
    # unmatchable as bracket candidates).
    canonical = json.dumps(
        dict(bindings),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
    return bool(
        isinstance(binding_evidence, Mapping)
        and binding_evidence.get("schema_version")
        == "joulewise.instrument_binding_evidence.v1"
        and binding_evidence.get("binding_vector_sha256")
        bracket_slot=observation.bracket_slot,
        bracket_window_id=observation.bracket_window_id,
        bracket_plan_id=observation.bracket_plan_id,
        bracket_plan_sha256=observation.bracket_plan_sha256,
        bracket_evidence_root_id=observation.bracket_evidence_root_id,
        bracket_runs_root=observation.bracket_runs_root,
    )


def discover_calibration_candidates(
    ledger_snapshot: CalibrationLedgerSnapshot,
) -> tuple[CalibrationCandidate, ...]:
    """Enumerate valid endpoints from the sole ledger authority.

    The mechanism closes workflow omission, unregistered evidence, and
    rollback/stale-head consumption; it does not defend against a malicious
    trusted writer or a rewrite of both Git and full ledger history.
    """

    if (
        not isinstance(ledger_snapshot, CalibrationLedgerSnapshot)
        or not ledger_snapshot.valid
        and not ledger_snapshot.is_governed_open_bracket_extension
    ):
        return ()
    finalized_session_ids = {
        session.session_id
        for session in ledger_snapshot.bracket_sessions
        if session.state == "finalized"
    }
    candidates: list[CalibrationCandidate] = []
    for observation in ledger_snapshot.observations:
        if (
            observation.disposition != "valid"
            or observation.is_historical_import
            or observation.bracket_session_id is not None
            and observation.bracket_session_id not in finalized_session_ids
        ):
            continue
        candidate = _candidate_from_observation(observation)
        if candidate is None:
            return ()
        candidates.append(candidate)
    return tuple(candidates)


def _prior_set_matches_import_cutoff_prefix(
    artifact: Mapping[str, Any],
    ledger_snapshot: CalibrationLedgerSnapshot,
) -> bool:
    """Bind issuance prior-set data to the import-marked cutoff prefix."""

    cutoff = artifact["ledger_cutoff"]
    prefix = tuple(
        observation
        for observation in ledger_snapshot.observations
        if observation.sequence <= cutoff["sequence"]
    )
    # The checked-in schema fixture predates issuance and deliberately has a
    # genesis cutoff. Production issuance, or any fixture containing imported
    # prefix rows, must satisfy the exact marker-bound comparison below.

exec
/bin/zsh -lc "rg -n \"76 receipts|sequence.?76|historical import|historical-import|38 historical|30 valid|systematic-invalid|ordinary-invalid|calibration_observation_ledger\" tests configs scripts docs/process_traces/2026-08-07-d117-plan-freeze -g '*.py' -g '*.json' -g '*.jsonl' -g '*.md' | head -n 600; find tests/fixtures -maxdepth 3 -type f | sort | rg 'calibr|ledger|d117|fiducial'" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 exited 1 in 0ms:
docs/process_traces/2026-08-07-d117-plan-freeze/DESIGN-MEMO.md:131:Ideal no-failure receipt evolution from the issued sequence-76 head is three receipts per window—session capability, pre finalization, post finalization—ending at sequence 85 after all three windows. Exact sequence numbers are arm-time facts, not desk-frozen plan literals.
docs/process_traces/2026-08-07-d117-plan-freeze/DESIGN-MEMO.md:165:I recommend deriving a successor from all content-distinct, valid, same-epoch observations through the chosen cutoff. Systematic, ordinary-invalid, aborted, or unresolved attempts remain recorded but excluded. The lead should explicitly ratify that corpus rule because D-102 establishes the successor obligation but does not fully spell out this live-prefix derivation policy.
docs/process_traces/2026-08-07-d117-plan-freeze/DESIGN-MEMO.md:407:The fixture begins with the exact issued-ledger semantics: 76 receipts, including 38 historical import observations—30 valid, 2 systematic, 6 ordinary-invalid. Candidate discovery must exclude every import-marked observation.
scripts/calibration_ledger_bootstrap.py:62:    "ordinary-invalid": 6,
scripts/calibration_ledger_bootstrap.py:63:    "systematic-invalid": 2,
scripts/calibration_ledger_bootstrap.py:239:            "by the authenticated historical-import cutoff"
scripts/calibration_ledger_bootstrap.py:396:        help="explicit ruled historical-import table",
tests/test_calibration_bracketing.py:184:        ("systematic-invalid", 2),
tests/test_calibration_bracketing.py:185:        ("ordinary-invalid", 6),
tests/test_calibration_bracketing.py:221:                "ordinary-invalid": 6,
tests/test_calibration_bracketing.py:222:                "systematic-invalid": 2,
tests/test_calibration_bracketing.py:259:            observation_kind="historical-import",
tests/test_calibration_bracketing.py:618:            ledger = repo / "runs" / "calibration_observation_ledger.jsonl"
tests/test_calibration_bracketing.py:752:            observation_kind="historical-import",
tests/test_calibration_bracketing.py:799:            observation_kind="historical-import",
scripts/calibration_ledger_backfill.py:61:        else "ordinary-invalid"
scripts/validate_powermetrics_fiducial.py:664:    disposition = "ordinary-invalid"
scripts/validate_powermetrics_fiducial.py:667:            "systematic-invalid"
tests/test_calibration_ledger.py:256:            ("20260101T000002-bbbbbbbb", "2", "systematic-invalid"),
tests/test_calibration_ledger.py:257:            ("20260101T000003-cccccccc", "3", "ordinary-invalid"),
configs/calibration/calibration_acceptance_d079_v2.json:12:    "reason": "D-109 R2 raw-physics and artifact-hash verification is bound by the authenticated historical-import cutoff"
configs/calibration/calibration_acceptance_d079_v2.json:17:    "ledger_schema": "joulewise.calibration_observation_ledger.v1",
configs/calibration/calibration_acceptance_d079_v2.json:189:      "ledger_schema": "joulewise.calibration_observation_ledger.v1"
configs/calibration/calibration_acceptance_d079_v2.json:218:        "disposition": "ordinary-invalid",
configs/calibration/calibration_acceptance_d079_v2.json:320:        "disposition": "ordinary-invalid",
configs/calibration/calibration_acceptance_d079_v2.json:332:        "disposition": "systematic-invalid",
configs/calibration/calibration_acceptance_d079_v2.json:344:        "disposition": "ordinary-invalid",
configs/calibration/calibration_acceptance_d079_v2.json:404:        "disposition": "ordinary-invalid",
configs/calibration/calibration_acceptance_d079_v2.json:410:        "disposition": "ordinary-invalid",
configs/calibration/calibration_acceptance_d079_v2.json:416:        "disposition": "ordinary-invalid",
configs/calibration/calibration_acceptance_d079_v2.json:428:        "disposition": "systematic-invalid",
configs/calibration/calibration_acceptance_d079_v2.json:436:      "ordinary-invalid": 6,
configs/calibration/calibration_acceptance_d079_v2.json:437:      "systematic-invalid": 2,
configs/calibration/calibration_ledger_head.json:4:  "ledger_schema": "joulewise.calibration_observation_ledger.v1"

exec
/bin/zsh -lc "ls -l runs/calibration_observation_ledger.jsonl configs/calibration/calibration_ledger_head.json 2>/dev/null; wc -l runs/calibration_observation_ledger.jsonl 2>/dev/null; head -n 2 runs/calibration_observation_ledger.jsonl 2>/dev/null; tail -n 2 runs/calibration_observation_ledger.jsonl 2>/dev/null; sed -n '1,120p' configs/calibration/calibration_ledger_head.json; sed -n '1,280p' tests/test_calibration_bracketing.py" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
-rw-r--r--@ 1 edr  wheel  172 Aug  7 09:02 configs/calibration/calibration_ledger_head.json
{
  "sequence": 76,
  "head_digest": "08456d5076c18a9a7f758969b02f5b6f7ad9fcc267dd12e2d3778c22458094d7",
  "ledger_schema": "joulewise.calibration_observation_ledger.v1"
}
"""Defect-shaped regressions for claim-bearing calibration bracketing."""

from __future__ import annotations

import base64
import hashlib
import json
import math
from dataclasses import replace
from decimal import Decimal
from pathlib import Path
import subprocess
import tempfile
from types import MappingProxyType, SimpleNamespace
import unittest
from unittest.mock import patch
import zlib

from joulewise.calibration_bracketing import (
    ACCEPTANCE_BOUND_SCHEMA,
    DEFAULT_ACCEPTANCE_BOUND_PATH,
    ISSUED_ACCEPTANCE_BOUND_SHA256,
    CalibrationCandidate,
    _canonical_sha256,
    _valid_acceptance_bound,
    calibration_bracket_for_bundles,
    discover_calibration_candidates,
    evaluate_calibration_bracket as _evaluate_calibration_bracket,
    load_calibration_acceptance_bound,
    load_calibration_candidate,
)
from joulewise.calibration_ledger import (
    DEFAULT_HEAD_PIN_PATH,
    GENESIS_DIGEST,
    LEDGER_SCHEMA,
    CalibrationLedgerSnapshot,
    LedgerObservation,
    bootstrap_historical_import,
    content_id_from_artifact_hashes,
    load_calibration_ledger_snapshot,
)
from joulewise.powermetrics_fiducial import (
    MAX_AGE_S,
    PROTOCOL_ID,
    PROTOCOL_V2_ID,
    PROTOCOL_V3_SHA256,
    PULSE_COUNT,
    REGION_COVERAGE_RESOLUTION_S,
    RESIDUAL_REGION_METHOD,
    V2_BINDING_FIELDS,
)
from joulewise.schemas import CalibrationBracketingPolicy
from scripts.calibration_ledger_bootstrap import (
    _issued_acceptance_artifact,
    _issued_artifact_bytes,
)


_REAL_D079_TABLE = Path("/private/tmp/d079-ledger-dispositions.json")
_REAL_D079_CUSTODY_MANIFEST = Path(
    "/private/tmp/d079-custody-manifest.lead.json"
)
_REAL_D079_TABLE_SHA256 = (
    "5da820aa5c649e5991b934230cd75e8c99daa8dcea22f3f1b3e3db89c80f2a6a"
)
_REAL_D079_CUSTODY_MANIFEST_SHA256 = (
    "99cbf3df7aef3b81839f40272a529eb137bf2f21276e2a1d07788c764035f078"
)
_UNISSUED_ACCEPTANCE_FIXTURE_SHA256 = (
    "9a264c57fdc007de473872870f19a5e1c9bd9b11256c25266b0e3e50ebba0ceb"
)
_UNISSUED_ACCEPTANCE_FIXTURE_B85 = b"""
c-qZd*={3Ac75-!AoSD?7pr4m#!oh827a(-fI-_YMk8?};zlXExoDWAstb+!cc0)+i4;Y(3UC2cDv_BPH}1L1Igt^+e>WQ44f&p@
)IIWI=;yP$KaK8wnXe}NxgYprrb(X`w8R%3<;)LDnq}_Nd^IZ{AJxa&|F&E$_~WCz`_P_sbWLB{ql)mcyYQ4p)y-tw+*mmGZFt-
^;J*LGXZZBbV=2`7g6%Ky4*&moGt^?)SIWz7F`sZ7YCDguN!@DJ55tPf=K1aaZBShJ`{r@Ol9sDB*4=8>Y^yz&-
Oalp^Mv|o$CLh3pVos^nhd=Ca=|og{I#}h^ba+{^{atLezf3!uKEQJqX|<P!L@jNUOQkkucHNh9zEQD8TveoXjVq|G~DCb#C5*l(
Zgb1R(XBx-
fE2abv=&>mruOt@@hG+^=L8}k2lj3Tl4NQa##9KJS>}y;t&4Wxnyg=#@UyHWu69JJZ}EKxn&n4&2wACc2Ird84vx?&F0IFy2Jdt-
TZg+-
MgVLJX`k5FC9P3^ZmgO^Px+tezFcdW&aw?ZpeFDl+T2*rt`v+_Vs^Jmi9y3UGOmfjA=d0Cw>0XzNXyW_n+>&_2;{b2AV!h`q`(hp
Do+;Cf&3}kQ6(o!`c0mmh(lo;K%-
uPq@CD%!i>HRtTg=o*bS4kInKul3{Pj3NhBau$<@lWSd88Gp4*;AZEJF6}5+(dOYD#9~^_*h6jfC9vLPS1l|UOgNuL?&k8L%{_UY
(w7Je!lgV~$JpWUJ_ZYs#YJ=7<E5L}fD$P%e9&_BM;0#kjOz@<_s^#73!w&g;3>?yJQo4LkvroHp+nB$ZHJ*O(W%{z@XP3_Sa|i$
Rr2{Ih+-x75>0upIm>zO#*iHqxy*Rx;&leA?p)2!-$k5freA>y_E$5vMr=tvCh9!c1+2^iOKWPt#F%!5E$pu$%MS-
|qA}1Eiv%B@JKkvZYO=!3$WnJ@QWU5isV5N4fw8_>n=~|06Ix6xyYpIJN5mlyCwFuQ#OH^wlEz>@W4*toA>B9iO?`+>^=8q@Qvx}
RL59>fzlC$*LCnaTM8@*(ga@Da!6=jLSm!yrS<cOS((Iu%VXr~1m?MWYebr^4joLwvlF^&v<Y|v!h4(Gj*s>o<kGCKQOv-
Vm?silpQrIKD~FH6wH31cGXR3vE*KIRxg_UDG90?ZL;C-dBmr-
NXoU@I4utrXf&E~$E%3X$<9hmwu3x@JW(1xLYTVUrfH(Puh09ujM{pOBR@1QSc4SaQ-XnX0p`<XjcfJMXf~M#7~=IHgF{0@qnpwU
p90X*comb)Uh9ob5ItdR*lvoVVG0w~qbMF22T(dbExFeIr@k^N4@TlU3m|`rOaT{PXzVN9#1kjnpqb;A^DsXqP*qO*P%dR~tpf?J
rZFrqfj3h1vegZKYB|IpLN1Ng8Xl9dk4?2POB8Y!jKU7O3h4Eixm3*M3~AW<$5J5=~(Dlpp)quw1OBFmRLYYtQ`nnnBW`Lay7q_$
UBshyih>oYhL1<IATs>nn2VC{r29S+a}~aT2vNrIu`UOd9!Xh-
;3~S6?|7CbC5rFPu;T!4()u;*TGHG>=_I9E~JRAfF7v#&TuExkL8Zj5NzBW{KQz$P|gxiB43fOhA&BfCx&Olc&4wKwm$+8Xb5{hB
0DRctr0_=&0Ajb9t0A@F--4aB#IU0<Mkj3O*uORY+1vqKHzI(I{d@rQ&=+t#Va4jLXa@HZ`%VJ_4HTz4S&2BVUhC@=mkGbA?vc7S
Ab3cpr)Ga?XW96d|Qp5L=OwQQ(8xYGJAsl~CMo$EQt1iLq?ODrIpKKKj-
8yfDhS^wClY6fGT$cHXON>BDfgq~O^SfT=bMqu2l_bd-
={LN8E&g)<R(6lmm*sAxqNRnn##;L#}XH5ym6RjROYNl1#KsF;Lts!EOY638)%u2iiPWgo4G1#>}<p|`+erSfCMR&`F&P4Ji-
;JG-;x%5%!twMP1g*6WIzJgB#x$vPT6tfgvt|16%6MR?$S~97|HWWN&g9k0~0r>-
J;ziBYvLO3<e1x;eyr|l}<SL<R$1G&7K2eZPYYqAlax2LRq`*qlQ~Y0M@(2mk>D%#9N^3Qa7{q3&zZE{0M>(557Ou1o6)r^lxt2c
F8&1VmL10THtPc*&2x;O%VqJ@m-WpX(EIu>HQ7JxITV-+_vNf-Vhmkls6f2ypqDo~$F+SCdZYFAy)!0DJgGWVcfQC>49MF-
bY*P)D-vAHFsEFgBoKaT#o8YlKc=T0xE{}39eZ0f;&{85Ox6#2~!N-E`kut2k7pN@)q!s<EWc-HWg655W!J<?^q_lSqT$5{H4>zW
YA2;CB61zexlw5Id^s0g+qZ>g$WFJan(5T;jTmOU(G9(lM3S^8a{#JbSPeOsChB4{@xO$G?1fLg2Ifsw&R%?Sa5)xHW`78Kjw0#|
%BT%VIBC#X3S(N~`R#0UOG!@%gtXD}Tsj5<$UDF}nqs*1p<Ku!ua#-jV78!!rK)|s9{f~iFq!MB>-
d6|CX1pjaK;J1So*EjHl=%(#SS73+7qE<w1AQxeE{}2!ACT0>4O~R4z~8Ivtu{B*fcB$^grf{!v<wL%M||1RsB$Hc>D(l-
jJAT~Q}Jl)EYuD7fD#6d4mGW~3PC10;Ag1WC=YQIBjO<=tia@Ta-gBsOCd!Ho(#VQ9~ls(Zfp=xQ6+N|KJL}{yfDhy`lg(cPJ|Gw
u}WUcpF~wwR2rnF^2D*CvXM42X#i~rZ34_GS_%H^!Pbj&s+eG0ChG#ld`tdBV_l(S8OewYw52B0OrwFBG>s3U<$&R#>?znG)tcc$
jyWJ#${X+jSw!P5!Z4~Oe=B@0k8-xYStuW;W0Oi2C|$z`@Y@XXB%M@HI_zb#35-
g5lssEdBV}X|2lQ)*l~}=w!KYC5(5evXug9lqBqk<MMJQ;E)~@vqCWYj2HZhY)Y;-
ooO6%Detw8lt(?n53a&N)MdM(B&gZM~uTYd94;B#@5v-
Pd5+u&9OGGUFmh7S}7qm?)S5gd3@($!bZLZ%3zN{o`Eye+1*UM5*tj*_5>G;>ly+(56r%&5FoXDBP3qZ1_taJhsb@o>;hVnRvN(L
<xceu7p-gR+j3Y0C$<<D(!PO&l|x>>&oe5k4=Ba<;yCU=)H15`;q7Yy1re7A;WB5Cs`R$Q1<^=SrwLlCd6-
gO)GJzzB41TU7*G0o}%ptYy4Gp5mDSxtFpIkU-jiz>z5#WFaU{&Vm#A&?+88a<Zy1hc!>srsk^XE%<;axv`d}x)N{0C)|L~#Zk_#
?f@5OCDc+|Jh1u-
KBei=9I{9`%Vbo{ma`Jj!qnOj3+NRnNE4xZBjkt?kyUm%8Bj1^`38QiV~v`?)RbZ&gl_A7##f;rZoo)@kBU)>j8+IDE~G}KgDyp$
niPb-6(94HkWlJz3`vJ#Y1KEu=fzRZ);Dxo2d&o@;iS4IPfacYj&?#biAE1m&8mT-
N4jcCRRADDLN!HI(FW0y+WI$(CThvu0uO^Rm*~Mq94IsDXF)JjYpT)CMeq&C(U2OavCv}~V4)f!RRudn$lVH${R!1qqHz;6o0RD`
c^Y@{n3v&sag=lLXl0}g63SGy8?MpotWfX0Z9Li{Uz~)*uNjiG_=KtlMXYOyNk&K>@L-
DwY44mYR0%pszM;I~K2%+*$;;wEn}ZV;dNeo%Di9JHkw!U1rs!5nvjjL1It-
dvmMRm!0Us$L1;+w}F?*lC6+V|oIfqXO5ljq)Lj<UOeXae-Bv5zOpvd-iPg@<qs>y<CgV~u>3{_~6nuP}wW=P8H6=EH7B|y*KK(7
I`PG~zIXRR*=bTVbZouh}*Nm-E%R|E21BifJmV5|5SstElG+4Tl|P?Dt@3&;bsF#E0Wxjf1_d?G}tLasqm;D@+I-
?Gku+Y$jpddi>&wggBNG8&i}i@!qU_AWCS!JvguA~84zX%z|pyn()fQ(KT{(2<f2>Zg<$%vk^x*_Pj2B+Rd9DxmS0td}ksNT#Y#)
3q)127JI|5!ppo;T_+Gj}$wA>{Wm+4|7)k1P_c*!y#u-
wy!N;SFm0P4+X*t85Gc<+pi3_L6?GO*!IE);T@Vh@#G828iaqVxvb6Ua>ljwH?$qD2@0qtN0?PEwup$j1|h6;a)CvAu@RwxjTN4w
%d)J4q|t;o0OZhu{W$t;b0YW60J=QPS%M%SQ6bee*f=8a8i9+!qy&e9JS$3u92IVBI2MWoDX3j>s%<S`>w-
gX4<3cHX?}7pd2z!6HmI4FfTfD2qBF*+x<C#?UX@fE88A=<QhHw~6jV};E1VXAL9{EWJwThi8%Mio+BTQt%`gKmkG9gB?!r2|59^
!l#QLLqvA#Qs$h$nBEt_xmyJ)7oyq~XQa^vOiGtK6+9*^yQ8RoO^e?J4r$M(&KT_CJ~`#NfScSf6M3_tv^-@DQ_8g!YKG?{-
ocHnxy;OVBW7dLjjYIE1CH+a2jlh=D~^!g*4y$-
>;L+}XXlU*7|&~8{E88j_s?`u(63Ia=n$TFx01$qkXx+;hIi8>caQISZ=l0h0}Va4$14!ooNo!f0A_^lrv=0kt7MWuaC%Oy`Ame+
QO9O~l}tI@m(R;RX%mN^7ubFHZ5(C^R{qT-
2yQNjf17nltB_9{!)idq9Y%ly7pKiSi8(P}6(l`Fw<5kf>pQ0#)P9?=VBFw9EBHbc@El~B8ydIC7Lt>rY4S>M&_r*HZ%TU|Vd7^D
yEn~*k8URqPz`k*C94)~1^mQr$Fk}9UHSEA>D@t9a`d+qqHR-
e8Azi2fG14CrG6sRpkrU<8&XtdAF!DuB+2qjxc`CN4>;OAi3E?W)30-
gWPzJBsr_@dQTM1?E_qnE0pS3ywwCL%aMxN;Ic3+S`zp!+OA1_&zzDNsb?3Vfa4*Xk#4OD|_*V^jj!=CV^!fR|dd>=;M{p+SRE&E
N@A2`yE7c?{j^BI_Uuv<_nG9j$);4)LPZOt7|EMv{34H&#S&2}&W3JqWx7FC<3!z*m-
A;Zs>45pqq?Owg(CYxR>iYZt9<n_)uns=YtXt?FrHFDf8Ya%_aNus1aZTvav3!&nr`QW5QyDAw|>RzH2;bU8v=rpc&dB8Vvb^cqn
Sj5CaohS*_~WFbKwu>>va6d^hgB|;c>CBCoKPu{{@t|5dl@S55Sc8<C2^Fzmh8$+=uC(a_ylMPXTwOUSX;TSp^1zu!{E5kcmefn<
VqSZ!*(zbn&)1{zFBx1=askV7H;8~EBRa<yBMFTYp3?O6?bqK+>7dOAF)lXOKFIo+Lo=nQxXfVUv+-
?Zno6yKZgbtP#lR`ig=Tj@E)?sdKEhMruC^GMC_31kHMXR+XMt6ov_mC~YIvImvB(Rr|nTjQ$uiL!dBgoD%`g|fQjkK6s$@(3we!
jYU(dtxvR?@e%^I8dV2LYR`Mw2N?u=AiL6=pNlOy0-R-
WQ?t39oagKE0>a&lf!}S}jFok!nSWMvGJsoK<C{LyKOHH35cHyao+3goJIay}c-gRtH%WoZr{#Crg2s;~Ejf2xAl5Qnf+h6T(-
WwY5oSRSL+5_8h&C2~{cK!YE9YZ2_yjdw5@~pDd7F<{`2wQ_;_}1s5TUKCP`WAgCs_r6>eQ+d9L6QMnoQC`9M+HwZuygLz-
8pR5{Pv>Lr7W)wEzDgv0G2oNJuRsa-
{e`H)xMcdL&G+;hKWpJzLJ!({>^$PcUTK!}x<)ye@@1=~WkisCqAtJo<nGAST+hd7zR4F5hQCdn{qBqJ|L&kyvpbFk(b%KyB<NNu
f%va0j)^87BjeniZKhO4;JzWJs6aTgLlL_?tth6<xYp3Y;*LCyR<jejr-Tu>l_6UD$)~<fvdiGBvtv<AMp53qR>){B^v-
4nSGS9zqyKK2w9S-EJ58ajS_`F>+tsTM}V}@MX(Yx{S(YxIdrg1xicXCkgU-A8y5oX21eDa7}H!F3c_0YrNXx{E<*y@270~ZY6m-
W26we!3635?;1EZ@bA`>Czy=r}e}f=<+<(=>-GK%<o!v&gJ<-
LA&}d~{wU_fwj5=gxY~R#SYMyMd=PTVl@ZfZ5)#T}YhpZ#?B;Kab6)4cC6y-m+hvnf9}Ox|+UX$MOEs+qO^NP3gCj5iahT-Cudz{
@=UxDX{(HrGU^y0_ydCeXEX6eodKX?QqwCP~EQmoi0fsP*=Qvw;dtP^!kmP23bGZyFQ_`S(RF}W3vd5<EI{9xc<JaJnfF${p0Wd{
kK1N|M74C`Pc3*|MQo>jh6G#KM{4y)pUeGpZ<}f;n_;_W;F{FF0Y=8Q0PvWf_7Gm_QL4@&0H{6={J=i+HU!I-
WBBY9!wFSU2TB&L1h*GXoK6yo$>jd(5g{O=R_1XYOv$e)zK5rtz9)dTeIB6l~mosgfb5=Iru2(&bszwxOFAj9E{EL=>sj=qT{<b`
q;%M)7?GsB=hIx+`|tZo}>KH`q*h&pkMI*IOK^NHr3_03LVPU$7iMI<1Sf`rn{ZW0rWPL;|tcFK1uMCH+{R3xI2S<u=~ip=OS-
=$aAx(`wnwERJtp(I{<chnnz_a3i0Ooo`%7$o$qfsiTYERFF5>y<F47=ihGyZLB%DdNjuAnlo}3RLGQ39>H4fI9Nk>d)0Z!#`u<*
;Oy-~0^kSDvc-r^-
^TXTce0VzXAI>I0%b}C!z!Tl^OSKQ+Y0HyOe)yN;w>F#M4mKU)<gRtRvd;O8VcJV2dHE3O(KfUU`mU48K|*~wlt~o%3{}$JY|Eww
xssE@c(^y)B&{zRG*l=P+v(Q3@4kNbfA+zM4g
"""


def _unissued_acceptance_fixture_bytes() -> bytes:
    """Return the exact pre-issuance fixture bytes, independent of repo state."""

    encoded = b"".join(_UNISSUED_ACCEPTANCE_FIXTURE_B85.split())
    raw = zlib.decompress(base64.b85decode(encoded))
    assert hashlib.sha256(raw).hexdigest() == _UNISSUED_ACCEPTANCE_FIXTURE_SHA256
    return raw


def _unissued_acceptance_fixture() -> dict:
    artifact = json.loads(_unissued_acceptance_fixture_bytes())
    assert _valid_acceptance_bound(artifact)
    return artifact


def _synthetic_issued_artifact() -> dict:
    """Return a schema-valid issued artifact for isolated consumer tests."""

    artifact = _unissued_acceptance_fixture()
    prior = artifact["prior_observation_set"]
    observations = [
        row for row in prior["observations"] if row["disposition"] == "valid"
    ]
    assert len(observations) == 19
    additions = (
        ("valid", 11),
        ("systematic-invalid", 2),
        ("ordinary-invalid", 6),
    )
    for disposition, count in additions:
        for index in range(count):
            token = f"synthetic-issued-{disposition}-{index}"
            observations.append(
                {
                    "content_id": hashlib.sha256(token.encode()).hexdigest(),
                    "epoch_id": "d079_epoch",
                    "disposition": disposition,
                    "attempt_id": token,
                }
            )
    head_digest = hashlib.sha256(b"synthetic-issued-head").hexdigest()
    artifact["schema_version"] = ACCEPTANCE_BOUND_SCHEMA
    artifact["artifact_role"] = "issued"
    artifact["issuance"] = {
        "status": "issued",
        "claim_eligible": True,
        "reason": "synthetic issued-artifact consumer regression",
    }
    artifact["ledger_cutoff"] = {
        "sequence": 76,
        "head_digest": head_digest,
        "ledger_schema": LEDGER_SCHEMA,
        "role": "issued_acceptance_baseline",
    }
    prior["cutoff"] = {
        key: artifact["ledger_cutoff"][key]
        for key in ("sequence", "head_digest", "ledger_schema")
    }
    prior["observations"] = observations
    artifact["backfill_candidate"].update(
        {
            "status": "issued",
            "candidate_inventory": {
                "ordinary-invalid": 6,
                "systematic-invalid": 2,
                "valid": 30,
            },
            "production_issuance_blocked": False,
            "required_verification": "complete: synthetic consumer regression",
        }
    )
    artifact["derivation_sha256"] = _canonical_sha256(
        {
            key: value
            for key, value in artifact.items()
            if key != "derivation_sha256"
        }
    )
    assert _valid_acceptance_bound(artifact)
    return artifact


def _synthetic_issued_snapshot(
    artifact: dict,
) -> CalibrationLedgerSnapshot:
    epoch = artifact["prior_observation_set"]["epoch_catalog"]["d079_epoch"]
    observations = tuple(
        LedgerObservation(
            sequence=2 * index,
            receipt_digest=hashlib.sha256(
                f"issued-receipt-{index}".encode()
            ).hexdigest(),
            attempt_id=row["attempt_id"],
            content_id=row["content_id"],
            artifact_sha256=MappingProxyType({}),
            identity_epoch=MappingProxyType(dict(epoch)),
            t1_bindings=MappingProxyType({field: None for field in V2_BINDING_FIELDS}),
            capture_wall_time_s="1.0",
            exact_bound_lexeme_s="0.025",
            disposition=row["disposition"],
            custody_locator=f"/synthetic-issued/{row['attempt_id']}",
            observation_kind="historical-import",
        )
        for index, row in enumerate(
            artifact["prior_observation_set"]["observations"], start=1
        )
    )
    cutoff = artifact["ledger_cutoff"]
    return CalibrationLedgerSnapshot(
        ledger_schema=LEDGER_SCHEMA,
        ledger_path=Path("synthetic-issued-ledger.jsonl"),
        head_sequence=cutoff["sequence"],
        head_digest=cutoff["head_digest"],
        receipts=(),
        observations=observations,
        refusal_reasons=(),
        baseline_sequence=cutoff["sequence"],
        baseline_digest=cutoff["head_digest"],
    )


def _fixture_snapshot(
    candidates: list[CalibrationCandidate],

exec
/bin/zsh -lc 'rg -n "''^def (bootstrap_historical_import|build_historical|plan_historical|prepare_historical|validate_historical)" joulewise/calibration_ledger.py scripts/calibration_ledger_bootstrap.py; sed -n '"'120,360p' scripts/calibration_ledger_bootstrap.py; sed -n '1500,2050p' joulewise/calibration_ledger.py" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
joulewise/calibration_ledger.py:1221:def prepare_historical_import(
joulewise/calibration_ledger.py:1499:def bootstrap_historical_import(
    staging_path: Path | None = None
    try:
        staging_descriptor, staging_name = tempfile.mkstemp(
            prefix=f".{destination.name}.issued-",
            dir=destination.parent,
        )
        staging_path = Path(staging_name)
        staging = os.fdopen(staging_descriptor, "wb")
        staging_descriptor = -1
        with staging:
            _write_issued_artifact_payload(staging, payload)
            staging.flush()
            os.fsync(staging.fileno())
        os.replace(staging_path, destination)
        staging_path = None
    finally:
        if staging_descriptor >= 0:
            os.close(staging_descriptor)
        if staging_path is not None:
            try:
                staging_path.unlink()
            except FileNotFoundError:
                pass


def _issued_acceptance_artifact(
    plan: Any,
    source_artifact: Mapping[str, Any],
    *,
    source_artifact_raw: bytes | None = None,
) -> dict[str, Any]:
    """Build the D-079 issued artifact only from the prepared ledger prefix."""

    if source_artifact_raw is None:
        authenticated_source = _authenticated_explicit_acceptance_bound(
            source_artifact
        )
    else:
        authenticated_source = _acceptance_bound_from_authenticated_bytes(
            source_artifact_raw
        )
        if (
            authenticated_source is not None
            and dict(source_artifact) != authenticated_source
        ):
            authenticated_source = None
    if authenticated_source is None:
        raise ValueError(
            "acceptance artifact source does not match its role-indexed byte pin"
        )
    if (
        plan.final_sequence != _D079_ISSUANCE_SEQUENCE
        or plan.head_digest != _D079_ISSUANCE_HEAD_DIGEST
        or len(plan.receipts) != _D079_ISSUANCE_SEQUENCE
    ):
        raise ValueError("ledger plan is not the ruled D-079 issuance cutoff")
    if any(
        receipt.get("event")
        not in {
            HISTORICAL_IMPORT_RESERVATION_EVENT,
            HISTORICAL_IMPORT_FINALIZATION_EVENT,
        }
        for receipt in plan.receipts
    ):
        raise ValueError("issued prior set requires an import-only ledger prefix")

    # Clone the authenticated source, not the caller's mapping. This preserves
    # the reviewed schema-field order that defines the issued file pin and
    # makes output independent of caller key insertion order.
    artifact = json.loads(
        json.dumps(dict(authenticated_source), allow_nan=False)
    )
    epoch_catalog = artifact["prior_observation_set"]["epoch_catalog"]
    observations: list[dict[str, Any]] = []
    for receipt in plan.receipts:
        if receipt["event"] != HISTORICAL_IMPORT_FINALIZATION_EVENT:
            continue
        epoch_ids = [
            epoch_id
            for epoch_id, epoch in epoch_catalog.items()
            if dict(epoch) == dict(receipt["identity_epoch"])
        ]
        if len(epoch_ids) != 1:
            raise ValueError("ledger observation does not map to one artifact epoch")
        observations.append(
            {
                "content_id": receipt["content_id"],
                "epoch_id": epoch_ids[0],
                "disposition": receipt["disposition"],
                "attempt_id": receipt["attempt_id"],
            }
        )
    disposition_counts = {
        disposition: sum(
            observation["disposition"] == disposition
            for observation in observations
        )
        for disposition in sorted(_D079_ISSUANCE_INVENTORY)
    }
    if (
        len(observations) != 38
        or disposition_counts != _D079_ISSUANCE_INVENTORY
        or len({row["content_id"] for row in observations}) != len(observations)
        or len({row["attempt_id"] for row in observations}) != len(observations)
    ):
        raise ValueError("ledger prefix does not have the ruled 30/2/6 inventory")

    cutoff = {
        "sequence": plan.final_sequence,
        "head_digest": plan.head_digest,
        "ledger_schema": LEDGER_SCHEMA,
    }
    artifact["schema_version"] = ACCEPTANCE_BOUND_SCHEMA
    artifact["artifact_role"] = "issued"
    artifact["issuance"] = {
        "status": "issued",
        "claim_eligible": True,
        "reason": (
            "D-109 R2 raw-physics and artifact-hash verification is bound "
            "by the authenticated historical-import cutoff"
        ),
    }
    artifact["ledger_cutoff"] = {
        **cutoff,
        "role": "issued_acceptance_baseline",
    }
    artifact["prior_observation_set"]["cutoff"] = cutoff
    artifact["prior_observation_set"]["observations"] = observations
    artifact["backfill_candidate"].update(
        {
            "status": "issued",
            "candidate_inventory": disposition_counts,
            "production_issuance_blocked": False,
            "required_verification": (
                "complete: lead-owned raw-physics and artifact-hash verification"
            ),
        }
    )
    artifact["derivation_sha256"] = _canonical_sha256(
        {
            key: value
            for key, value in artifact.items()
            if key != "derivation_sha256"
        }
    )
    if not _valid_acceptance_bound(artifact):
        raise ValueError("deterministically emitted acceptance artifact is invalid")
    return artifact


def _prepare_issued_acceptance_artifact(
    plan: Any,
    source_artifact: Mapping[str, Any],
    *,
    source_artifact_raw: bytes | None = None,
) -> PreparedIssuedAcceptanceArtifact:
    """Build and fully validate the exact artifact bytes before any commit."""

    artifact = _issued_acceptance_artifact(
        plan,
        source_artifact,
        source_artifact_raw=source_artifact_raw,
    )
    expected_cutoff = {
        "sequence": plan.final_sequence,
        "head_digest": plan.head_digest,
        "ledger_schema": LEDGER_SCHEMA,
    }
    expected_observations = []
    epoch_catalog = artifact["prior_observation_set"]["epoch_catalog"]
    for receipt in plan.receipts:
        if receipt["event"] != HISTORICAL_IMPORT_FINALIZATION_EVENT:
            continue
        epoch_ids = [
            epoch_id
            for epoch_id, epoch in epoch_catalog.items()
            if dict(epoch) == dict(receipt["identity_epoch"])
        ]
        if len(epoch_ids) != 1:
            raise ValueError("ledger observation does not map to one artifact epoch")
        expected_observations.append(
            {
                "content_id": receipt["content_id"],
                "epoch_id": epoch_ids[0],
                "disposition": receipt["disposition"],
                "attempt_id": receipt["attempt_id"],
            }
        )
    core = {
        key: value
        for key, value in artifact.items()
        if key != "derivation_sha256"
    }
    if artifact["derivation_sha256"] != _canonical_sha256(core):
        raise ValueError("issued artifact whole-core digest is invalid")
    if artifact["ledger_cutoff"] != {
        **expected_cutoff,
        "role": "issued_acceptance_baseline",
    }:
        raise ValueError("issued artifact cutoff does not match the import plan")
    if artifact["prior_observation_set"]["cutoff"] != expected_cutoff:
        raise ValueError("issued prior-set cutoff does not match the import plan")
    if (
        artifact["prior_observation_set"]["observations"]
        != expected_observations
    ):
        raise ValueError("issued prior set is not the complete import prefix")
    raw = _issued_artifact_bytes(artifact)
    artifact_file_sha256 = hashlib.sha256(raw).hexdigest()
    if artifact_file_sha256 != ISSUED_ACCEPTANCE_BOUND_SHA256:
        raise ValueError("issued artifact bytes do not match the reviewed byte pin")
    derivation_sha256 = artifact["derivation_sha256"]
    output_record = {
        "schema_version": ISSUED_ARTIFACT_OUTPUT_SCHEMA,
        "record": "issued-acceptance-artifact",
        "artifact": artifact,
        "derivation_sha256": derivation_sha256,
        "artifact_file_sha256": artifact_file_sha256,
        "artifact_file_content": raw.decode("utf-8"),
    }
    return PreparedIssuedAcceptanceArtifact(
        artifact_file_bytes=raw,
        artifact_file_sha256=artifact_file_sha256,
        derivation_sha256=derivation_sha256,
        output_record_bytes=canonical_json_bytes(output_record) + b"\n",
        summary_fields=(
            ("issued_artifact_derivation_sha256", derivation_sha256),
            ("issued_artifact_file_sha256", artifact_file_sha256),
        ),
    )


def _emit(
    plan: Any,
    *,
    executed: bool,
    outcome: str,
    prepared_issued_artifact: PreparedIssuedAcceptanceArtifact | None = None,
) -> None:
    for receipt in plan.receipts:
        sys.stdout.buffer.write(
    ledger_path: Path,
    *,
    head_pin_path: Path,
    roots: Sequence[Path] = (),
    checkout_root: Path = REPO_ROOT,
    disposition_table_raw: bytes,
    expected_disposition_table_sha256: str,
    custody_manifest_raw: bytes,
    expected_custody_manifest_sha256: str,
    execute: bool = False,
    require_committed_pin: bool = True,
    repo_root: Path = REPO_ROOT,
) -> HistoricalImportPlan:
    """Prepare, and only when requested atomically append, the genesis import.

    Dry-run is the default and creates no path. Execution stages and fsyncs the
    complete chain outside the reader-visible ledger path, then atomically
    replaces the empty ledger. The head pin is never written.
    """

    ledger = Path(ledger_path)
    pin = Path(head_pin_path)
    _require_genesis_bootstrap_state(
        ledger,
        pin,
        require_committed_pin=require_committed_pin,
        repo_root=Path(repo_root),
        allow_nonempty_pending_plan=execute,
    )
    plan = prepare_historical_import(
        roots=roots,
        checkout_root=checkout_root,
        disposition_table_raw=disposition_table_raw,
        expected_disposition_table_sha256=expected_disposition_table_sha256,
        custody_manifest_raw=custody_manifest_raw,
        expected_custody_manifest_sha256=expected_custody_manifest_sha256,
    )
    if not execute:
        return plan

    payload = plan.ledger_bytes
    ledger.parent.mkdir(parents=True, exist_ok=True)
    lock_descriptor = _open_ledger_lock(ledger)
    try:
        fcntl.flock(lock_descriptor, fcntl.LOCK_EX)
        ledger_descriptor = os.open(
            ledger, os.O_RDWR | os.O_CREAT | os.O_APPEND, 0o600
        )
        os.close(ledger_descriptor)
        already_committed = _require_genesis_bootstrap_state(
            ledger,
            pin,
            require_committed_pin=require_committed_pin,
            repo_root=Path(repo_root),
            expected_payload=payload,
        )
        _reauthenticate_historical_import_plan(plan)
        if already_committed:
            try:
                _fsync_parent_directory(ledger.parent)
            except OSError as exc:
                raise HistoricalImportDurabilityUncertain(plan) from exc
            return plan

        staging_descriptor = -1
        staging_path: Path | None = None
        try:
            try:
                staging_descriptor, staging_name = tempfile.mkstemp(
                    prefix=f".{ledger.name}.bootstrap-",
                    dir=ledger.parent,
                )
                staging_path = Path(staging_name)
                staging = os.fdopen(staging_descriptor, "wb")
                staging_descriptor = -1
                with staging:
                    _write_bootstrap_payload(staging, payload)
                    staging.flush()
                    os.fsync(staging.fileno())
                os.replace(staging_path, ledger)
                staging_path = None
            except Exception as exc:
                raise CalibrationLedgerError(
                    "historical import append failed atomically"
                ) from exc
            try:
                _fsync_parent_directory(ledger.parent)
            except OSError as exc:
                raise HistoricalImportDurabilityUncertain(plan) from exc
        finally:
            if staging_descriptor >= 0:
                os.close(staging_descriptor)
            if staging_path is not None:
                try:
                    staging_path.unlink()
                except FileNotFoundError:
                    pass
    finally:
        try:
            os.close(lock_descriptor)
        except OSError:
            pass
    return plan


def _locked_append(
    ledger_path: Path,
    build: Any,
) -> Mapping[str, Any]:
    ledger_path = Path(ledger_path)
    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    lock_descriptor = _open_ledger_lock(ledger_path)
    try:
        fcntl.flock(lock_descriptor, fcntl.LOCK_EX)
        descriptor = os.open(
            ledger_path, os.O_RDWR | os.O_CREAT | os.O_APPEND, 0o600
        )
        try:
            with os.fdopen(descriptor, "r+b", closefd=False) as handle:
                handle.seek(0)
                raw = handle.read()
                receipts, reasons = _parse_ledger(raw)
                if reasons:
                    raise CalibrationLedgerError(", ".join(sorted(reasons)))
                receipt = build(receipts)
                if not _valid_receipt_shape(receipt):
                    raise CalibrationLedgerError(
                        "writer constructed a malformed receipt"
                    )
                payload = canonical_json_bytes(receipt) + b"\n"
                handle.seek(0, os.SEEK_END)
                handle.write(payload)
                handle.flush()
                os.fsync(handle.fileno())
                return _frozen_mapping(receipt)
        finally:
            os.close(descriptor)
    finally:
        os.close(lock_descriptor)


def append_pending_receipt(
    ledger_path: Path,
    *,
    attempt_id: str,
    custody_locator: str,
    identity_epoch: Mapping[str, Any] | None = None,
    t1_bindings: Mapping[str, Any] | None = None,
    head_pin_path: Path = DEFAULT_HEAD_PIN_PATH,
    require_committed_pin: bool = True,
    repo_root: Path = REPO_ROOT,
) -> Mapping[str, Any]:
    """Reserve an attempt before any capture directory or sampler exists.

    This closes workflow omission, unregistered evidence, and rollback or
    stale-head consumption; it does not defend against a malicious trusted
    writer or a rewrite of both Git and the full ledger history.
    """

    if not isinstance(attempt_id, str) or not attempt_id:
        raise CalibrationLedgerError("attempt_id must be nonempty")
    pin_path = Path(head_pin_path)
    try:
        pin_raw = pin_path.read_bytes()
        pin_value = json.loads(pin_raw)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise CalibrationLedgerError("head pin is unreadable") from exc
    pin = _head_pin(pin_value)
    if pin is None:
        raise CalibrationLedgerError("head pin is malformed")
    if require_committed_pin and _committed_pin_bytes(pin_path, repo_root) != pin_raw:
        raise CalibrationLedgerError("head pin is not committed at Git HEAD")

    def build(receipts: Sequence[Mapping[str, Any]]) -> Mapping[str, Any]:
        sequence = len(receipts) + 1
        predecessor = receipts[-1]["receipt_digest"] if receipts else GENESIS_DIGEST
        if (len(receipts), predecessor) != pin:
            raise CalibrationLedgerError(
                "physical ledger head differs from the committed pin"
            )
        observations, reasons = _attempts_and_observations(receipts)
        del observations
        if reasons or any(row["attempt_id"] == attempt_id for row in receipts):
            raise CalibrationLedgerError(
                ", ".join(sorted(reasons or {"calibration_ledger_attempt_conflict"}))
            )
        return _new_receipt(
            sequence=sequence,
            predecessor_digest=str(predecessor),
            event="reservation",
            attempt_id=attempt_id,
            content_id=None,
            artifacts={},
            identity_epoch=identity_epoch,
            t1_bindings=t1_bindings,
            capture_wall_time_s=None,
            exact_bound_lexeme_s=None,
            disposition="pending",
            custody_locator=custody_locator,
        )

    return _locked_append(Path(ledger_path), build)


def finalize_attempt_receipt(
    ledger_path: Path,
    *,
    attempt_id: str,
    disposition: str,
    custody_locator: str,
    artifact_sha256: Mapping[str, str] | None = None,
    identity_epoch: Mapping[str, Any] | None = None,
    t1_bindings: Mapping[str, Any] | None = None,
    capture_wall_time_s: str | None = None,
    exact_bound_lexeme_s: str | None = None,
) -> Mapping[str, Any]:
    """Append the sole final state for a previously reserved attempt."""

    if disposition not in FINAL_DISPOSITIONS:
        raise CalibrationLedgerError(f"invalid final disposition: {disposition!r}")
    artifacts = dict(artifact_sha256 or {})
    content_id = content_id_from_artifact_hashes(artifacts)

    def build(receipts: Sequence[Mapping[str, Any]]) -> Mapping[str, Any]:
        reservations = [
            row
            for row in receipts
            if row["attempt_id"] == attempt_id and row["event"] == "reservation"
        ]
        finals = [
            row
            for row in receipts
            if row["attempt_id"] == attempt_id and row["event"] == "finalization"
        ]
        if len(reservations) != 1 or finals:
            raise CalibrationLedgerError("attempt is not uniquely pending")
        reservation = reservations[0]
        normalized_epoch = _normalized_vector(
            identity_epoch, IDENTITY_EPOCH_FIELDS
        )
        normalized_t1 = _normalized_vector(t1_bindings, T1_FIELDS)
        if (
            dict(reservation["identity_epoch"]) != normalized_epoch
            or dict(reservation["t1_bindings"]) != normalized_t1
            or reservation["custody_locator"] != custody_locator
        ):
            raise CalibrationLedgerError(
                "finalization conflicts with the reserved attempt binding"
            )
        predecessor = receipts[-1]["receipt_digest"] if receipts else GENESIS_DIGEST
        return _new_receipt(
            sequence=len(receipts) + 1,
            predecessor_digest=str(predecessor),
            event="finalization",
            attempt_id=attempt_id,
            content_id=content_id,
            artifacts=artifacts,
            identity_epoch=identity_epoch,
            t1_bindings=t1_bindings,
            capture_wall_time_s=capture_wall_time_s,
            exact_bound_lexeme_s=exact_bound_lexeme_s,
            disposition=disposition,
            custody_locator=custody_locator,
        )

    return _locked_append(Path(ledger_path), build)


def head_pin_for_receipt(receipt: Mapping[str, Any]) -> dict[str, Any]:
    """Emit the exact candidate pin that must be reviewed and committed."""

    if not _valid_receipt_shape(receipt):
        raise CalibrationLedgerError("cannot pin a malformed receipt")
    return {
        "sequence": int(receipt["sequence"]),
        "head_digest": str(receipt["receipt_digest"]),
        "ledger_schema": LEDGER_SCHEMA,
    }


__all__ = [
    "ALL_DISPOSITIONS",
    "CONTENT_ID_ARTIFACTS",
    "DEFAULT_HEAD_PIN_PATH",
    "DEFAULT_LEDGER_PATH",
    "FINAL_DISPOSITIONS",
    "GENESIS_DIGEST",
    "GOVERNED_ARTIFACTS",
    "HISTORICAL_IMPORT_EVENT_PREFIX",
    "HISTORICAL_IMPORT_CUSTODY_MANIFEST_SCHEMA",
    "HISTORICAL_IMPORT_FINALIZATION_EVENT",
    "HISTORICAL_IMPORT_RESERVATION_EVENT",
    "HISTORICAL_IMPORT_TABLE_SCHEMA",
    "IDENTITY_EPOCH_FIELDS",
    "LEDGER_SCHEMA",
    "RECEIPT_SCHEMA",
    "REFUSAL_TAXONOMY",
    "CalibrationLedgerError",
    "CalibrationLedgerSnapshot",
    "HistoricalImportDurabilityUncertain",
    "HistoricalImportPlan",
    "LedgerObservation",
    "append_pending_receipt",
    "artifact_hashes",
    "bootstrap_historical_import",
    "custody_manifest_bytes",
    "canonical_sha256",
    "content_id_from_artifact_hashes",
    "finalize_attempt_receipt",
    "generate_historical_custody_manifest",
    "head_pin_for_receipt",
    "load_calibration_ledger_snapshot",
    "prepare_historical_import",
]

exec
/bin/zsh -lc "git show impl/d117-u1-ledger-session:joulewise/calibration_ledger.py | sed -n '900,1245p'; git show impl/d117-u1-ledger-session:tests/test_calibration_ledger.py | sed -n '80,280p;560,850p'; git show impl/d117-u1-ledger-session:tests/test_calibration_bracketing.py | sed -n '820,1235p'" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
            reasons.add("calibration_ledger_malformed")
            continue
        if not _valid_receipt_shape(value):
            reasons.add("calibration_ledger_malformed")
            continue
        if (
            value["sequence"] != expected_sequence
            or value["predecessor_digest"] != predecessor
            or value["receipt_digest"] in seen_digests
        ):
            reasons.add("calibration_ledger_chain_conflict")
        expected_sequence += 1
        predecessor = value["receipt_digest"]
        seen_digests.add(predecessor)
        receipts.append(value)
    return receipts, reasons


def _observation_from_receipt(
    receipt: Mapping[str, Any],
    *,
    observation_kind: str,
    session: Mapping[str, Any] | None = None,
) -> LedgerObservation:
    content_id = receipt.get("content_id")
    return LedgerObservation(
        sequence=int(receipt["sequence"]),
        receipt_digest=str(receipt["receipt_digest"]),
        attempt_id=str(receipt["attempt_id"]),
        content_id=str(content_id) if isinstance(content_id, str) else None,
        artifact_sha256=MappingProxyType(dict(receipt["artifact_sha256"])),
        identity_epoch=MappingProxyType(dict(receipt["identity_epoch"])),
        t1_bindings=MappingProxyType(dict(receipt["t1_bindings"])),
        capture_wall_time_s=receipt.get("capture_wall_time_s"),
        exact_bound_lexeme_s=receipt.get("exact_bound_lexeme_s"),
        disposition=str(receipt["disposition"]),
        custody_locator=str(receipt["custody_locator"]),
        observation_kind=observation_kind,
        bracket_session_id=(str(session["session_id"]) if session else None),
        bracket_slot=(str(receipt["slot"]) if session else None),
        bracket_window_id=(str(session["window_id"]) if session else None),
        bracket_plan_id=(str(session["plan_id"]) if session else None),
        bracket_plan_sha256=(str(session["plan_sha256"]) if session else None),
        bracket_evidence_root_id=(
            str(session["evidence_root_id"]) if session else None
        ),
        bracket_runs_root=(str(session["runs_root"]) if session else None),
    )


def _session_identity_matches(
    receipt: Mapping[str, Any], open_receipt: Mapping[str, Any]
) -> bool:
    return all(receipt.get(field) == open_receipt.get(field) for field in _SESSION_IDENTITY_KEYS)


def _bracket_sessions_and_observations(
    receipts: Sequence[Mapping[str, Any]],
) -> tuple[list[CalibrationBracketSession], list[LedgerObservation], set[str]]:
    states: dict[str, dict[str, Any]] = {}
    claimed_attempts: set[str] = set()
    reasons: set[str] = set()
    for receipt in receipts:
        if receipt.get("schema_version") != BRACKET_SESSION_SCHEMA:
            continue
        event = receipt["event"]
        session_id = str(receipt["session_id"])
        if event == BRACKET_SESSION_OPEN_EVENT:
            slots = receipt["slots"]
            attempt_ids = {str(slots[role]["attempt_id"]) for role in BRACKET_SESSION_SLOTS}
            if session_id in states or attempt_ids & claimed_attempts:
                reasons.add("calibration_ledger_bracket_session_conflict")
                continue
            claimed_attempts.update(attempt_ids)
            states[session_id] = {
                "open": receipt,
                "claims": {},
                "finals": {},
                "abort": None,
            }
            continue
        state = states.get(session_id)
        if state is None:
            reasons.add("calibration_ledger_bracket_session_conflict")
            continue
        open_receipt = state["open"]
        if not _session_identity_matches(receipt, open_receipt):
            reasons.add("calibration_ledger_bracket_session_conflict")
            continue
        claims = state["claims"]
        finals = state["finals"]
        if event == BRACKET_SESSION_SLOT_CLAIM_EVENT:
            slot = str(receipt["slot"])
            expected_slot = (
                BRACKET_SESSION_SLOTS[len(finals)] if len(finals) < 2 else None
            )
            reserved = open_receipt["slots"].get(slot)
            if (
                state["abort"] is not None
                or slot != expected_slot
                or slot in claims
                or slot in finals
                or not isinstance(reserved, Mapping)
                or receipt["attempt_id"] != reserved["attempt_id"]
            ):
                reasons.add("calibration_ledger_bracket_session_conflict")
                continue
            claims[slot] = receipt
            continue
        if event == BRACKET_SESSION_FINALIZATION_EVENT:
            slot = str(receipt["slot"])
            expected_slot = BRACKET_SESSION_SLOTS[len(finals)] if len(finals) < 2 else None
            reserved = open_receipt["slots"].get(slot)
            if (
                state["abort"] is not None
                or slot != expected_slot
                or slot in finals
                or not isinstance(reserved, Mapping)
                or receipt["attempt_id"] != reserved["attempt_id"]
                or receipt["custody_locator"] != reserved["custody_locator"]
                or dict(receipt["identity_epoch"]) != dict(reserved["identity_epoch"])
                or dict(receipt["t1_bindings"]) != dict(reserved["t1_bindings"])
            ):
                reasons.add("calibration_ledger_bracket_session_conflict")
                continue
            finals[slot] = receipt
            continue
        finalized_slots = list(finals)
        unused_slots = [slot for slot in BRACKET_SESSION_SLOTS if slot not in finals]
        if (
            event != BRACKET_SESSION_ABORT_EVENT
            or state["abort"] is not None
            or len(finals) == 2
            or receipt["finalized_slots"] != finalized_slots
            or receipt["unused_slots"] != unused_slots
        ):
            reasons.add("calibration_ledger_bracket_session_conflict")
            continue
        state["abort"] = receipt

    sessions: list[CalibrationBracketSession] = []
    completed_observations: list[LedgerObservation] = []
    for session_id, state in sorted(
        states.items(), key=lambda item: int(item[1]["open"]["sequence"])
    ):
        open_receipt = state["open"]
        finals = state["finals"]
        abort = state["abort"]
        if abort is not None:
            session_state = "aborted"
        elif len(finals) == 2:
            session_state = "finalized"
        else:
            session_state = "open"
            reasons.add("calibration_ledger_bracket_session_open")
        finalized_observations = {
            slot: _observation_from_receipt(
                receipt,
                observation_kind=(
                    "bracket-session-finalized"
                    if session_state == "finalized"
                    else "bracket-session-aborted"
                ),
                session=open_receipt,
            )
            for slot, receipt in finals.items()
        }
        # R2's observation universe contains finalized evidence from every
        # terminal governed session, including a PRE whose session later
        # aborts.  An open session is intentionally withheld until its state
        # is governed-terminal; candidate discovery applies the narrower
        # finalized-session rule separately.
        if session_state in {"finalized", "aborted"}:
            completed_observations.extend(
                finalized_observations[slot]
                for slot in BRACKET_SESSION_SLOTS
                if slot in finalized_observations
            )
        sessions.append(
            CalibrationBracketSession(
                session_id=session_id,
                window_id=str(open_receipt["window_id"]),
                plan_id=str(open_receipt["plan_id"]),
                plan_sha256=str(open_receipt["plan_sha256"]),
                evidence_root_id=str(open_receipt["evidence_root_id"]),
                runs_root=str(open_receipt["runs_root"]),
                capability_receipt_digest=str(open_receipt["receipt_digest"]),
                capability_sequence=int(open_receipt["sequence"]),
                slot_attempt_ids=MappingProxyType(
                    {
                        slot: str(open_receipt["slots"][slot]["attempt_id"])
                        for slot in BRACKET_SESSION_SLOTS
                    }
                ),
                state=session_state,
                finalized_slots=MappingProxyType(finalized_observations),
                abort_receipt_digest=(
                    str(abort["receipt_digest"]) if abort is not None else None
                ),
                abort_reason=(str(abort["reason"]) if abort is not None else None),
            )
        )
    return sessions, completed_observations, reasons


def _attempts_and_observations(
    receipts: Sequence[Mapping[str, Any]],
) -> tuple[list[LedgerObservation], list[CalibrationBracketSession], set[str]]:
    pending: dict[str, Mapping[str, Any]] = {}
    finalized: dict[str, Mapping[str, Any]] = {}
    reasons: set[str] = set()
    for receipt in receipts:
        if receipt.get("schema_version") == BRACKET_SESSION_SCHEMA:
            continue
        attempt_id = str(receipt["attempt_id"])
        if receipt["event"] in {
            "reservation",
            HISTORICAL_IMPORT_RESERVATION_EVENT,
        }:
            if attempt_id in pending or attempt_id in finalized:
                reasons.add("calibration_ledger_attempt_conflict")
            else:
                pending[attempt_id] = receipt
            continue
        reservation = pending.get(attempt_id)
        expected_final_event = (
            HISTORICAL_IMPORT_FINALIZATION_EVENT
            if reservation is not None
            and reservation["event"] == HISTORICAL_IMPORT_RESERVATION_EVENT
            else "finalization"
        )
        if (
            reservation is None
            or attempt_id in finalized
            or receipt["event"] != expected_final_event
        ):
            reasons.add("calibration_ledger_attempt_conflict")
        else:
            finalized[attempt_id] = receipt
    if set(pending) - set(finalized):
        reasons.add("calibration_ledger_pending")

    observations: list[LedgerObservation] = []
    content_classification: dict[str, tuple[str, tuple[tuple[str, Any], ...]]] = {}
    for attempt_id, receipt in sorted(
        finalized.items(), key=lambda item: int(item[1]["sequence"])
    ):
        content_id = receipt.get("content_id")
        epoch = dict(receipt["identity_epoch"])
        if isinstance(content_id, str):
            classification = (
                (
                    "unresolved"
                    if receipt["disposition"] == "abandoned"
                    else str(receipt["disposition"])
                ),
                tuple((field, epoch.get(field)) for field in IDENTITY_EPOCH_FIELDS),
            )
            previous = content_classification.get(content_id)
            if previous is not None and previous != classification:
                reasons.add("calibration_ledger_content_conflict")
            content_classification[content_id] = classification
        observations.append(
            _observation_from_receipt(
                receipt,
                observation_kind=(
                    "historical-import"
                    if receipt["event"] == HISTORICAL_IMPORT_FINALIZATION_EVENT
                    else "live-capture"
                ),
            )
        )
    sessions, session_observations, session_reasons = (
        _bracket_sessions_and_observations(receipts)
    )
    reasons.update(session_reasons)
    session_attempt_ids = {
        attempt_id
        for session in sessions
        for attempt_id in session.slot_attempt_ids.values()
    }
    if set(pending) & session_attempt_ids:
        reasons.add("calibration_ledger_bracket_session_conflict")
    observations.extend(session_observations)
    content_classification.clear()
    classification_observations = list(observations)
    visible_attempts = {observation.attempt_id for observation in observations}
    classification_observations.extend(
        observation
        for session in sessions
        for observation in session.finalized_slots.values()
        if observation.attempt_id not in visible_attempts
    )
    for observation in classification_observations:
        if observation.content_id is None:
            continue
        classification = (
            observation.classification_disposition,
            tuple(
                (field, observation.identity_epoch.get(field))
                for field in IDENTITY_EPOCH_FIELDS
            ),
        )
        previous = content_classification.get(observation.content_id)
        if previous is not None and previous != classification:
            reasons.add("calibration_ledger_content_conflict")
        content_classification[observation.content_id] = classification
    observations.sort(key=lambda observation: observation.sequence)
    return observations, sessions, reasons


def _custody_reasons(
    observations: Sequence[LedgerObservation], repo_root: Path
) -> set[str]:
    for observation in observations:
        if not observation.artifact_sha256:
            if observation.disposition == "abandoned":
                continue
            return {"calibration_ledger_custody_invalid"}
        root = Path(observation.custody_locator)
        if not root.is_absolute():
            root = Path(repo_root) / root
        for relative, expected in observation.artifact_sha256.items():
            path = root / relative
            try:
                actual = hashlib.sha256(path.read_bytes()).hexdigest()
            except OSError:
                return {"calibration_ledger_custody_invalid"}
            if actual != expected:
                return {"calibration_ledger_custody_invalid"}
    return set()


def load_calibration_ledger_snapshot(
    ledger_path: Path = DEFAULT_LEDGER_PATH,
    head_pin_path: Path = DEFAULT_HEAD_PIN_PATH,
    *,
    baseline_sequence: int | None = None,
    baseline_digest: str | None = None,
    require_committed_pin: bool = True,
    verify_custody: bool = True,
    repo_root: Path = REPO_ROOT,
) -> CalibrationLedgerSnapshot:
    """Load, authenticate, and freeze exactly one ledger snapshot.

    A proper physical prefix of the pin is classified explicitly as rollback;
    "316113960c596a6f927987dbdf8f2bca4b0cca9ee4a59a540bbd32bba9048985"
)


class CalibrationLedgerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.ledger = self.root / "ledger.jsonl"
        self.pin = self.root / "head.json"
        self._write_pin(
            {
                "sequence": 0,
                "head_digest": GENESIS_DIGEST,
                "ledger_schema": LEDGER_SCHEMA,
            }
        )
        self.epoch = {
            "os_build": "25F84",
            "hardware_model": "Mac15,9",
            "power_policy": "ac_high_power",
            "sampling_interval_ms": 100,
            "estimator_revision": "joint_loss_sublevel_interval_branch_v2",
            "pulse_protocol_id": "powermetrics_pulse_fiducial_v3",
        }
        self.t1 = {field: f"value-{field}" for field in V2_BINDING_FIELDS}
        self.t1.update(self.epoch)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def _write_pin(self, value: dict) -> None:
        self.pin.write_text(json.dumps(value) + "\n", encoding="utf-8")

    def _isolated_cli_checkout(self) -> tuple[Path, Path]:
        """Copy the CLI into a tiny repo with a committed genesis head pin."""

        source_root = Path(__file__).resolve().parents[1]
        repo = self.root / "cli-repo"
        shutil.copytree(source_root / "joulewise", repo / "joulewise")
        (repo / "scripts").mkdir()
        shutil.copy2(
            source_root / "scripts" / "calibration_ledger_bootstrap.py",
            repo / "scripts" / "calibration_ledger_bootstrap.py",
        )
        pin = repo / "configs" / "calibration" / "calibration_ledger_head.json"
        pin.parent.mkdir(parents=True)
        pin.write_text(
            json.dumps(
                {
                    "sequence": 0,
                    "head_digest": GENESIS_DIGEST,
                    "ledger_schema": LEDGER_SCHEMA,
                }
            )
            + "\n",
            encoding="utf-8",
        )
        subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
        subprocess.run(
            ["git", "config", "user.email", "tests@joulewise.invalid"],
            cwd=repo,
            check=True,
        )
        subprocess.run(
            ["git", "config", "user.name", "JouleWise tests"],
            cwd=repo,
            check=True,
        )
        subprocess.run(
            ["git", "add", pin.relative_to(repo).as_posix()],
            cwd=repo,
            check=True,
        )
        subprocess.run(
            ["git", "commit", "-qm", "pin synthetic genesis head"],
            cwd=repo,
            check=True,
        )
        return repo / "scripts" / "calibration_ledger_bootstrap.py", pin

    def _custody(self, attempt_id: str) -> Path:
        path = self.root / "another-root" / "instrument_validation" / attempt_id
        (path / "raw").mkdir(parents=True)
        (path / "raw" / "powermetrics.plist").write_bytes(b"raw-" + attempt_id.encode())
        (path / "events.jsonl").write_text(
            '{"timestamp_s": 99.0}\n', encoding="utf-8"
        )
        (path / "instrument_evidence.json").write_text(
            json.dumps({"b_fiducial_s": 0.025, "attempt": attempt_id}) + "\n",
            encoding="utf-8",
        )
        (path / "manifest.json").write_text(
            json.dumps({"attempt": attempt_id}) + "\n", encoding="utf-8"
        )
        return path

    def _reserve(self, attempt_id: str, custody: Path):
        return append_pending_receipt(
            self.ledger,
            attempt_id=attempt_id,
            custody_locator=str(custody),
            identity_epoch=self.epoch,
            t1_bindings=self.t1,
            head_pin_path=self.pin,
            require_committed_pin=False,
        )

    def _finalize(self, attempt_id: str, custody: Path, disposition: str = "valid"):
        return finalize_attempt_receipt(
            self.ledger,
            attempt_id=attempt_id,
            disposition=disposition,
            custody_locator=str(custody),
            artifact_sha256=artifact_hashes(custody),
            identity_epoch=self.epoch,
            t1_bindings=self.t1,
            capture_wall_time_s="99.0",
            exact_bound_lexeme_s="0.025",
        )

    def _snapshot(self, *, verify_custody: bool = True):
        return load_calibration_ledger_snapshot(
            self.ledger,
            self.pin,
            baseline_sequence=0,
            baseline_digest=GENESIS_DIGEST,
            require_committed_pin=False,
            verify_custody=verify_custody,
        )

    def _open_bracket_session(self, session_id: str = "session-alpha"):
        return append_bracket_session_receipt(
            self.ledger,
            session_id=session_id,
            window_id="window-alpha",
            plan_id="plan-alpha",
            plan_sha256="a" * 64,
            evidence_root_id="evidence-alpha",
            runs_root=self.root / "another-root",
            slots={
                "pre": {
                    "attempt_id": f"{session_id}-pre",
                    "custody_locator": str(
                        self.root
                        / "another-root"
                        / "instrument_validation"
                        / f"{session_id}-pre"
                    ),
                    "identity_epoch": self.epoch,
                    "t1_bindings": self.t1,
                },
                "post": {
                    "attempt_id": f"{session_id}-post",
                    "custody_locator": str(
                        self.root
                        / "another-root"
                        / "instrument_validation"
                        / f"{session_id}-post"
                    ),
                    "identity_epoch": self.epoch,
                    "t1_bindings": self.t1,
                },
            },
            head_pin_path=self.pin,
            require_committed_pin=False,
        )

    def _finalize_bracket_slot(self, session_id: str, slot: str):
        attempt_id = f"{session_id}-{slot}"
        custody = (
            self.root / "another-root" / "instrument_validation" / attempt_id
        )
        if not custody.exists():
            custody = self._custody(attempt_id)
        return finalize_bracket_session_slot(
            self.ledger,
            session_id=session_id,
            slot=slot,
            disposition="valid",
            custody_locator=str(custody),
            artifact_sha256=artifact_hashes(custody),
            identity_epoch=self.epoch,
            t1_bindings=self.t1,
            capture_wall_time_s="99.0" if slot == "pre" else "111.0",
            exact_bound_lexeme_s="0.025",
        )

    def _historical_custody(
        self,
        checkout: Path,
        run_name: str,
        attempt_id: str,
        token: str,
    ) -> Path:
        custody = checkout / run_name / "instrument_validation" / attempt_id
        (custody / "raw").mkdir(parents=True)
        payloads = {
            "raw/powermetrics.plist": f"raw-{token}\n".encode(),
            "events.jsonl": (
                json.dumps({"event_type": "capture", "token": token}) + "\n"
    def test_finalization_is_single_transition(self) -> None:
        custody = self._custody("single")
        self._reserve("single", custody)
        self._finalize("single", custody)
        with self.assertRaisesRegex(CalibrationLedgerError, "uniquely pending"):
            self._finalize("single", custody)

    def test_missing_or_changed_custody_bytes_refuse(self) -> None:
        custody = self._custody("custody")
        self._reserve("custody", custody)
        final = self._finalize("custody", custody)
        self._write_pin(head_pin_for_receipt(final))
        (custody / "instrument_evidence.json").write_text("changed\n")
        snapshot = self._snapshot()
        self.assertEqual(
            snapshot.refusal_reasons,
            ("calibration_ledger_custody_invalid",),
        )

    def test_baseline_must_be_exact_member_of_current_chain(self) -> None:
        snapshot = load_calibration_ledger_snapshot(
            self.ledger,
            self.pin,
            baseline_sequence=1,
            baseline_digest="f" * 64,
            require_committed_pin=False,
        )
        self.assertIn("calibration_ledger_baseline_missing", snapshot.refusal_reasons)

    def test_bracket_session_happy_path_reserves_two_slots_under_one_pin(self) -> None:
        capability = self._open_bracket_session()
        self.assertEqual(capability["sequence"], 1)
        self.assertEqual(tuple(capability["slots"]), ("pre", "post"))
        self.assertEqual(
            {slot["expected_time_role"] for slot in capability["slots"].values()},
            {"pre", "post"},
        )

        pre = self._finalize_bracket_slot("session-alpha", "pre")
        self.assertEqual(pre["sequence"], 2)
        self.assertEqual(pre["event"], BRACKET_SESSION_FINALIZATION_EVENT)
        post = self._finalize_bracket_slot("session-alpha", "post")
        self.assertEqual(post["sequence"], 3)

        pin = terminal_head_pin_for_session(
            self.ledger, session_id="session-alpha"
        )
        self.assertEqual(pin["sequence"], post["sequence"])
        self.assertEqual(pin["head_digest"], post["receipt_digest"])
        self._write_pin(pin)
        snapshot = self._snapshot()
        self.assertEqual(snapshot.refusal_reasons, ())
        self.assertEqual(snapshot.head_sequence, 3)
        self.assertEqual(
            [observation.bracket_slot for observation in snapshot.observations],
            ["pre", "post"],
        )
        session = snapshot.bracket_session_by_id["session-alpha"]
        self.assertEqual(session.state, "finalized")
        self.assertEqual(set(session.finalized_slots), {"pre", "post"})

    def test_bracket_session_refuses_reordered_duplicate_and_conflicting_slots(
        self,
    ) -> None:
        self._open_bracket_session()
        post_custody = self._custody("session-alpha-post")
        with self.assertRaisesRegex(CalibrationLedgerError, "expected pre"):
            finalize_bracket_session_slot(
                self.ledger,
                session_id="session-alpha",
                slot="post",
                disposition="valid",
                custody_locator=str(post_custody),
                artifact_sha256=artifact_hashes(post_custody),
                identity_epoch=self.epoch,
                t1_bindings=self.t1,
                capture_wall_time_s="111.0",
                exact_bound_lexeme_s="0.025",
            )
        self._finalize_bracket_slot("session-alpha", "pre")
        with self.assertRaisesRegex(CalibrationLedgerError, "expected post"):
            self._finalize_bracket_slot("session-alpha", "pre")

        conflicting_t1 = dict(self.t1)
        conflicting_t1["power_policy"] = "battery"
        with self.assertRaisesRegex(CalibrationLedgerError, "reserved session binding"):
            finalize_bracket_session_slot(
                self.ledger,
                session_id="session-alpha",
                slot="post",
                disposition="valid",
                custody_locator=str(post_custody),
                artifact_sha256=artifact_hashes(post_custody),
                identity_epoch=self.epoch,
                t1_bindings=conflicting_t1,
                capture_wall_time_s="111.0",
                exact_bound_lexeme_s="0.025",
            )

    def test_generic_head_pin_refuses_session_open_and_pre_receipts(self) -> None:
        capability = self._open_bracket_session()
        with self.assertRaisesRegex(
            CalibrationLedgerError, "terminal_head_pin_for_session"
        ):
            head_pin_for_receipt(capability)
        pre = self._finalize_bracket_slot("session-alpha", "pre")
        with self.assertRaisesRegex(
            CalibrationLedgerError, "terminal_head_pin_for_session"
        ):
            head_pin_for_receipt(pre)

    def test_aborted_systematic_pre_remains_in_r2_universe_and_fires_trigger(
        self,
    ) -> None:
        self._open_bracket_session()
        custody = self._custody("session-alpha-pre")
        finalize_bracket_session_slot(
            self.ledger,
            session_id="session-alpha",
            slot="pre",
            disposition="systematic-invalid",
            custody_locator=str(custody),
            artifact_sha256=artifact_hashes(custody),
            identity_epoch=self.epoch,
            t1_bindings=self.t1,
            capture_wall_time_s="99.0",
            exact_bound_lexeme_s="0.035435840879704805",
        )
        abort_bracket_session(
            self.ledger,
            session_id="session-alpha",
            reason="pre_capture_systematic-invalid",
        )
        self._write_pin(
            terminal_head_pin_for_session(
                self.ledger, session_id="session-alpha"
            )
        )
        snapshot = self._snapshot()
        self.assertEqual(len(snapshot.observations), 1)
        self.assertEqual(snapshot.observations[0].disposition, "systematic-invalid")
        self.assertEqual(snapshot.bracket_sessions[0].state, "aborted")

        with mock.patch(
            "joulewise.calibration_bracketing.load_calibration_acceptance_bound",
            return_value=_unissued_acceptance_fixture(),
        ):
            result, reasons = evaluate_calibration_bracket(
                (),
                window_start_s=100.0,
                window_end_s=110.0,
                bindings=self.t1,
                policy=CalibrationBracketingPolicy(
                    require_bracket=True,
                    calibration_bracket_max_drift_s=0.010,
                ),
                ledger_snapshot=snapshot,
                _allow_unissued_fixture=True,
            )
        self.assertEqual(reasons, ("calibration_acceptance_bound_stale",))
        self.assertIn(
            "new_systematic_failure_challenges_preflight_screen",
            result["acceptance"]["prospective_rederivation"][
                "observed_triggers"
            ],
        )
    def test_open_session_refuses_until_governed_abort_and_never_deletes_partial(
        self,
    ) -> None:
        self._open_bracket_session()
        pre = self._finalize_bracket_slot("session-alpha", "pre")
        open_snapshot = self._snapshot()
        self.assertIn(
            "calibration_ledger_bracket_session_open",
            open_snapshot.refusal_reasons,
        )
        self.assertEqual(
            [observation.bracket_slot for observation in open_snapshot.observations],
            [],
        )

        closure = abort_bracket_session(
            self.ledger,
            session_id="session-alpha",
            reason="science_member_failed_before_post",
        )
        self.assertEqual(closure["event"], BRACKET_SESSION_ABORT_EVENT)
        self.assertEqual(closure["finalized_slots"], ("pre",))
        self.assertEqual(closure["unused_slots"], ("post",))
        self._write_pin(
            terminal_head_pin_for_session(
                self.ledger, session_id="session-alpha"
            )
        )
        snapshot = self._snapshot()
        self.assertEqual(snapshot.refusal_reasons, ())
        self.assertEqual(
            [observation.bracket_slot for observation in snapshot.observations],
            ["pre"],
        )
        self.assertEqual(
            snapshot.observations[0].observation_kind,
            "bracket-session-aborted",
        )
        session = snapshot.bracket_session_by_id["session-alpha"]
        self.assertEqual(session.state, "aborted")
        self.assertEqual(session.finalized_slots["pre"].receipt_digest, pre["receipt_digest"])
        with self.assertRaisesRegex(CalibrationLedgerError, "not open"):
            abort_bracket_session(
                self.ledger,
                session_id="session-alpha",
                reason="duplicate closure",
            )

    def test_bracket_session_open_requires_exact_committed_physical_head(self) -> None:
        self._open_bracket_session()
        with self.assertRaisesRegex(
            CalibrationLedgerError, "physical ledger head differs from the committed pin"
        ):
            self._open_bracket_session("session-beta")

    def test_bracket_reservation_cli_is_explicit_and_machine_readable(self) -> None:
        epoch_path = self.root / "epoch.json"
        t1_path = self.root / "t1.json"
        epoch_path.write_text(json.dumps(self.epoch), encoding="utf-8")
        t1_path.write_text(json.dumps(self.t1), encoding="utf-8")
        argv = [
            "--ledger",
            str(self.ledger),
            "--head-pin",
            str(self.pin),
            "--session-id",
            "session-cli",
            "--window-id",
            "window-cli",
            "--plan-id",
            "plan-cli",
            "--plan-sha256",
            "b" * 64,
            "--evidence-root-id",
            "evidence-cli",
            "--runs-root",
            str(self.root / "cli-runs"),
            "--pre-attempt-id",
            "session-cli-pre",
            "--post-attempt-id",
            "session-cli-post",
            "--pre-custody-locator",
            str(self.root / "cli-runs" / "instrument_validation" / "session-cli-pre"),
            "--post-custody-locator",
            str(self.root / "cli-runs" / "instrument_validation" / "session-cli-post"),
            "--identity-epoch-json",
            str(epoch_path),
            "--t1-bindings-json",
            str(t1_path),
            "--allow-uncommitted-pin-for-test",
        ]
        with mock.patch("sys.stdout", new_callable=io.StringIO) as stdout:
            self.assertEqual(bracket_session_cli.main(argv), 0)
        self.assertEqual(json.loads(stdout.getvalue())["status"], "validated_not_reserved")
        self.assertFalse(self.ledger.exists())

        with mock.patch("sys.stdout", new_callable=io.StringIO) as stdout:
            self.assertEqual(bracket_session_cli.main([*argv, "--execute"]), 0)
        output = json.loads(stdout.getvalue())
        self.assertEqual(output["status"], "reserved")
        self.assertEqual(output["receipt"]["event"], "bracket-session-open")
        self.assertEqual(output["terminal_head_pin"], None)
        self.assertTrue(self.ledger.is_file())

    def test_bracket_reservation_cli_dry_run_and_execute_share_malformed_input_refusal(
        self,
    ) -> None:
        epoch_path = self.root / "bad-cli-epoch.json"
        t1_path = self.root / "bad-cli-t1.json"
        epoch_path.write_text(json.dumps(self.epoch), encoding="utf-8")
        t1_path.write_text(json.dumps(self.t1), encoding="utf-8")
        runs_root = self.root / "bad-cli-runs"
        argv = [
            "--ledger", str(self.ledger),
            "--head-pin", str(self.pin),
            "--session-id", "session-bad-cli",
            "--window-id", "",
            "--plan-id", "plan-bad-cli",
            "--plan-sha256", "b" * 64,
            "--evidence-root-id", "evidence-bad-cli",
            "--runs-root", str(runs_root),
            "--pre-attempt-id", "session-bad-cli-pre",
            "--post-attempt-id", "session-bad-cli-post",
            "--pre-custody-locator",
            str(runs_root / "instrument_validation" / "session-bad-cli-pre"),
                bindings=self.bindings,
                policy=self.policy,
                ledger_snapshot=snapshot,
                _allow_unissued_fixture=True,
            )
        self.assertEqual(reasons, ("calibration_ledger_baseline_missing",))

    def candidate(
        self,
        name: str,
        capture_s: float,
        bound_s: Decimal | str | float,
        *,
        protocol_id: str = PROTOCOL_ID,
        bindings: dict | None = None,
    ) -> CalibrationCandidate:
        corpus_alias = {
            "pre": "20260722T145535-e941c821",
            "post": "20260722T194118-9dc0749d",
            "pre-v3": "20260722T214220-1acdbbc0",
            "post-v3": "20260722T215127-eeef661a",
        }
        new_observation = name in {
            "range-expander",
            "current-pre",
            "current-post",
            "window-b-new-systematic-pre",
            "window-b-post",
        }
        manifest_sha256 = (
            hashlib.sha256(f"manifest:{name}".encode()).hexdigest()
            if new_observation
            else "ab" * 32
        )
        evidence_sha256 = (
            hashlib.sha256(f"evidence:{name}".encode()).hexdigest()
            if new_observation
            else "cd" * 32
        )
        return CalibrationCandidate(
            relative_path=(
                f"instrument_validation/{corpus_alias.get(name, name)}"
            ),
            manifest_sha256=manifest_sha256,
            evidence_sha256=evidence_sha256,
            protocol_id=protocol_id,
            capture_wall_time_s=capture_s,
            b_fiducial_s=bound_s,
            bindings=self.bindings if bindings is None else bindings,
        )

    def _bound_session_fixture(self):
        specifications = (
            ("neighbor-pre", 98.0, "0.025", None, None, 1),
            ("neighbor-post", 112.0, "0.026", None, None, 2),
            ("session-pre", 99.0, "0.024", "session-alpha", "pre", 4),
            ("session-post", 111.0, "0.027", "session-alpha", "post", 5),
        )
        observations = []
        candidates = []
        for name, capture, bound, session_id, slot, sequence in specifications:
            manifest = hashlib.sha256(f"manifest:{name}".encode()).hexdigest()
            evidence = hashlib.sha256(f"evidence:{name}".encode()).hexdigest()
            hashes = {
                "manifest.json": manifest,
                "instrument_evidence.json": evidence,
            }
            content_id = content_id_from_artifact_hashes(hashes)
            receipt_digest = hashlib.sha256(f"receipt:{name}".encode()).hexdigest()
            attempt_id = f"attempt-{name}"
            candidate = replace(
                self.candidate(name, capture, bound),
                manifest_sha256=manifest,
                evidence_sha256=evidence,
                attempt_id=attempt_id,
                content_id=content_id,
                ledger_receipt_digest=receipt_digest,
                bracket_session_id=session_id,
                bracket_slot=slot,
                bracket_window_id="window-alpha" if session_id else None,
                bracket_plan_id="plan-alpha" if session_id else None,
                bracket_plan_sha256="a" * 64 if session_id else None,
                bracket_evidence_root_id="evidence-alpha" if session_id else None,
                bracket_runs_root="/synthetic/root-alpha" if session_id else None,
            )
            candidates.append(candidate)
            observations.append(
                LedgerObservation(
                    sequence=sequence,
                    receipt_digest=receipt_digest,
                    attempt_id=attempt_id,
                    content_id=content_id,
                    artifact_sha256=MappingProxyType(hashes),
                    identity_epoch=MappingProxyType(
                        {
                            field: self.bindings[field]
                            for field in (
                                "os_build",
                                "hardware_model",
                                "power_policy",
                                "sampling_interval_ms",
                                "estimator_revision",
                                "pulse_protocol_id",
                            )
                        }
                    ),
                    t1_bindings=MappingProxyType(dict(self.bindings)),
                    capture_wall_time_s=str(capture),
                    exact_bound_lexeme_s=bound,
                    disposition="valid",
                    custody_locator=f"/synthetic/{name}",
                    observation_kind=(
                        "bracket-session-finalized" if session_id else "live-capture"
                    ),
                    bracket_session_id=session_id,
                    bracket_slot=slot,
                    bracket_window_id="window-alpha" if session_id else None,
                    bracket_plan_id="plan-alpha" if session_id else None,
                    bracket_plan_sha256="a" * 64 if session_id else None,
                    bracket_evidence_root_id="evidence-alpha" if session_id else None,
                    bracket_runs_root=(
                        "/synthetic/root-alpha" if session_id else None
                    ),
                )
            )
        by_slot = {
            observation.bracket_slot: observation
            for observation in observations
            if observation.bracket_slot is not None
        }
        capability_digest = hashlib.sha256(b"capability-alpha").hexdigest()
        session = CalibrationBracketSession(
            session_id="session-alpha",
            window_id="window-alpha",
            plan_id="plan-alpha",
            plan_sha256="a" * 64,
            evidence_root_id="evidence-alpha",
            runs_root="/synthetic/root-alpha",
            capability_receipt_digest=capability_digest,
            capability_sequence=3,
            slot_attempt_ids=MappingProxyType(
                {slot: observation.attempt_id for slot, observation in by_slot.items()}
            ),
            state="finalized",
            finalized_slots=MappingProxyType(by_slot),
        )
        receipt_digests = [
            observations[0].receipt_digest,
            observations[1].receipt_digest,
            capability_digest,
            by_slot["pre"].receipt_digest,
            by_slot["post"].receipt_digest,
        ]
        snapshot = CalibrationLedgerSnapshot(
            ledger_schema=LEDGER_SCHEMA,
            ledger_path=Path("synthetic-session-ledger.jsonl"),
            head_sequence=5,
            head_digest=by_slot["post"].receipt_digest,
            receipts=tuple(
                MappingProxyType({"receipt_digest": digest})
                for digest in receipt_digests
            ),
            observations=tuple(sorted(observations, key=lambda item: item.sequence)),
            refusal_reasons=(),
            bracket_sessions=(session,),
            baseline_sequence=0,
            baseline_digest=GENESIS_DIGEST,
        )
        binding = build_calibration_bracket_binding(
            snapshot,
            session_id="session-alpha",
            window_id="window-alpha",
            plan_id="plan-alpha",
            plan_sha256="a" * 64,
            evidence_root_id="evidence-alpha",
            runs_root="/synthetic/root-alpha",
        )
        return snapshot, candidates, binding

    def test_exact_session_binding_selects_reserved_pair_not_neighbors(self) -> None:
        snapshot, candidates, binding = self._bound_session_fixture()
        resolved = validate_calibration_bracket_binding(
            binding,
            snapshot,
            window_id="window-alpha",
            plan_id="plan-alpha",
            plan_sha256="a" * 64,
            evidence_root_id="evidence-alpha",
            runs_root="/synthetic/root-alpha",
        )
        self.assertIsNotNone(resolved)
        with patch(
            "joulewise.calibration_bracketing.load_calibration_acceptance_bound",
            return_value=_unissued_acceptance_fixture(),
        ):
            result, reasons = _evaluate_calibration_bracket(
                candidates,
                window_start_s=100.0,
                window_end_s=110.0,
                bindings=self.bindings,
                policy=self.policy,
                ledger_snapshot=snapshot,
                bracket_binding=binding,
                bracket_window_id="window-alpha",
                bracket_plan_id="plan-alpha",
                bracket_plan_sha256="a" * 64,
                bracket_evidence_root_id="evidence-alpha",
                bracket_runs_root="/synthetic/root-alpha",
                _allow_unissued_fixture=True,
            )
        self.assertEqual(reasons, ())
        self.assertEqual(result["pre"]["attempt_id"], "attempt-session-pre")
        self.assertEqual(result["post"]["attempt_id"], "attempt-session-post")
        self.assertEqual(
            result["bracket_binding"]["binding_digest"],
            binding["binding_digest"],
        )

    def test_l5_later_same_t1_calibration_from_another_runs_root_cannot_be_borrowed(
        self,
    ) -> None:
        snapshot, candidates, binding = self._bound_session_fixture()
        later_other_root = replace(
            candidates[-1],
            relative_path="/synthetic/root-beta/instrument_validation/later-post",
            bracket_runs_root="/synthetic/root-beta",
        )
        supplied = [*candidates[:-1], later_other_root]
        with patch(
            "joulewise.calibration_bracketing.load_calibration_acceptance_bound",
            return_value=_unissued_acceptance_fixture(),
        ):
            _result, reasons = _evaluate_calibration_bracket(
                supplied,
                window_start_s=100.0,
                window_end_s=110.0,
                bindings=self.bindings,
                policy=self.policy,
                ledger_snapshot=snapshot,
                bracket_binding=binding,
                bracket_window_id="window-alpha",
                bracket_plan_id="plan-alpha",
                bracket_plan_sha256="a" * 64,
                bracket_evidence_root_id="evidence-alpha",
                bracket_runs_root="/synthetic/root-alpha",
                _allow_unissued_fixture=True,
            )
        self.assertEqual(reasons, ("calibration_ledger_off_ledger_artifact",))

        with patch(
            "joulewise.calibration_bracketing.load_calibration_acceptance_bound",
            return_value=_unissued_acceptance_fixture(),
        ):
            _result, reasons = _evaluate_calibration_bracket(
                candidates,
                window_start_s=100.0,
                window_end_s=110.0,
                bindings=self.bindings,
                policy=self.policy,
                ledger_snapshot=snapshot,
                bracket_binding=binding,
                bracket_window_id="window-alpha",
                bracket_plan_id="plan-alpha",
                bracket_plan_sha256="a" * 64,
                bracket_evidence_root_id="evidence-alpha",
                bracket_runs_root="/synthetic/root-beta",
                _allow_unissued_fixture=True,
            )
        self.assertEqual(reasons, ("calibration_bracket_binding_invalid",))

    def test_session_candidates_refuse_missing_neighbor_substituted_or_cross_window_binding(
        self,
    ) -> None:
        snapshot, candidates, binding = self._bound_session_fixture()
        self.assertIsNone(validate_calibration_bracket_binding(binding, snapshot))
        with patch(
            "joulewise.calibration_bracketing.load_calibration_acceptance_bound",
            return_value=_unissued_acceptance_fixture(),
        ):
            _result, reasons = _evaluate_calibration_bracket(
                candidates,
                window_start_s=100.0,
                window_end_s=110.0,
                bindings=self.bindings,
                policy=self.policy,
                ledger_snapshot=snapshot,
                _allow_unissued_fixture=True,
            )
        self.assertEqual(reasons, ("calibration_bracket_binding_missing",))

        substituted = json.loads(json.dumps(binding))
        substituted["endpoints"]["pre"] = {
            "attempt_id": candidates[0].attempt_id,
            "receipt_digest": candidates[0].ledger_receipt_digest,
            "content_digest": candidates[0].content_id,
        }
        substituted["binding_digest"] = _canonical_sha256(
            {
                key: value
                for key, value in substituted.items()
                if key != "binding_digest"
            }
        )
        self.assertIsNone(
            validate_calibration_bracket_binding(
                substituted,
                snapshot,
                window_id="window-alpha",
                plan_id="plan-alpha",
                plan_sha256="a" * 64,
                evidence_root_id="evidence-alpha",
                runs_root="/synthetic/root-alpha",
            )
        )

        cross_window = json.loads(json.dumps(binding))
        cross_window["window_id"] = "window-beta"
        cross_window["binding_digest"] = _canonical_sha256(
            {
                key: value
                for key, value in cross_window.items()
                if key != "binding_digest"
            }
        )
        self.assertIsNone(
            validate_calibration_bracket_binding(
                cross_window,
                snapshot,
                window_id="window-alpha",
                plan_id="plan-alpha",
                plan_sha256="a" * 64,
                evidence_root_id="evidence-alpha",
                runs_root="/synthetic/root-alpha",
            )
        )

    def test_open_and_aborted_session_observations_never_leak_as_candidates(self) -> None:
        snapshot, candidates, _binding = self._bound_session_fixture()
        session = snapshot.bracket_sessions[0]
        open_session = replace(
            session,
            state="open",
            finalized_slots=MappingProxyType({"pre": session.finalized_slots["pre"]}),
        )
        open_snapshot = replace(
            snapshot,
            observations=tuple(
                observation
                for observation in snapshot.observations
                if observation.bracket_slot != "post"
            ),
            bracket_sessions=(open_session,),
            head_sequence=4,
            head_digest=session.finalized_slots["pre"].receipt_digest,
            receipts=(
                *snapshot.receipts[:2],
                MappingProxyType(
                    {
                        "event": "bracket-session-open",
                        "session_id": "session-alpha",
                        "predecessor_digest": snapshot.receipts[1]["receipt_digest"],
                        "receipt_digest": session.capability_receipt_digest,
                    }
                ),
                MappingProxyType(
                    {
                        "event": "bracket-session-slot-finalization",
                        "session_id": "session-alpha",
                        "receipt_digest": session.finalized_slots["pre"].receipt_digest,
                    }
                ),
            ),
            refusal_reasons=(
                "calibration_ledger_bracket_session_open",
                "calibration_ledger_head_mismatch",
            ),
            committed_head_sequence=2,
            committed_head_digest=snapshot.receipts[1]["receipt_digest"],
        )
        by_attempt = {candidate.attempt_id: candidate for candidate in candidates}
        with patch(
            "joulewise.calibration_bracketing._candidate_from_observation",
            side_effect=lambda observation: by_attempt[observation.attempt_id],
        ):
            open_candidates = discover_calibration_candidates(open_snapshot)
        self.assertEqual(
            [candidate.bracket_session_id for candidate in open_candidates],
            [None, None],
        )

        aborted_session = replace(open_session, state="aborted")
        aborted_snapshot = replace(
            open_snapshot,
            # Keep the finalized PRE in the R2 observation universe.  The
            # discovery filter must consult governed session state instead of
            # laundering a synthetic snapshot by assuming observations were
            # pre-filtered by the loader.
            observations=open_snapshot.observations,
            bracket_sessions=(aborted_session,),
            refusal_reasons=(),
        )
        with patch(
            "joulewise.calibration_bracketing._candidate_from_observation",
            side_effect=lambda observation: by_attempt[observation.attempt_id],
        ):
            discovered = discover_calibration_candidates(aborted_snapshot)
        self.assertEqual(
            [candidate.bracket_session_id for candidate in discovered],
            [None, None],
        )

    def test_claim_window_passes_and_embeds_never_zero_allowance_once(self) -> None:
        # Exact H2 defect shape: a single sample maximum used to stand in for
        # temporal instrument stability. Two causal endpoints now bracket it.
        result, reasons = evaluate_calibration_bracket(
            [self.candidate("pre", 99.0, 0.020), self.candidate("post", 111.0, 0.027)],

exec
/bin/zsh -lc "python3 - <<'PY'
import json
from pathlib import Path
p=json.loads(Path('configs/calibration/calibration_acceptance_d079_v2.json').read_text())
print('schema',p.get('schema_version'))
print('cutoff',p.get('ledger_cutoff'))
print('counts',p.get('backfill_candidate',{}).get('candidate_inventory'))
print('operatives',p.get('decimal_derivation',{}).get('ratified_operatives'))
ms=p.get('derivation_corpus',{}).get('members',[])
vals=[m.get('b_fiducial_s') for m in ms]
print('members',len(ms),'min',min(vals),'max',max(vals))
print('epoch catalog',p.get('prior_observation_set',{}).get('epoch_catalog'))
print('triggers',p.get('prospective_rederivation',{}).get('triggers'))
PY
rg -n \"D-102|D-110|D-109|D-116|D-117\" docs/decision_log.md | head -n 100" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
schema joulewise.calibration_acceptance_bound.v2
cutoff {'sequence': 76, 'head_digest': '08456d5076c18a9a7f758969b02f5b6f7ad9fcc267dd12e2d3778c22458094d7', 'ledger_schema': 'joulewise.calibration_observation_ledger.v1', 'role': 'issued_acceptance_baseline'}
counts {'ordinary-invalid': 6, 'systematic-invalid': 2, 'valid': 30}
operatives {'bracket_screen_s': '0.010818', 'preflight_level_screen_s': '0.033558756679900', 'max_budgetable_excess_s': '0.001275166090593858', 'maximum_budgetable_drift_s': '0.012093166090593858', 'allowance_rule': 'max(observed_drift_s,bracket_screen_s)', 'operative_bound_rule': 'max(pre_b_fiducial_s,post_b_fiducial_s)+calibration_drift_allowance_s', 'embedding_count': 1}
members 19 min 0.022741007370546462 max 0.03355875667989999
epoch catalog {'d079_epoch': {'os_build': '25F84', 'hardware_model': 'Mac15,9', 'power_policy': 'ac_high_power', 'sampling_interval_ms': 100, 'estimator_revision': 'joint_loss_sublevel_interval_branch_v2', 'pulse_protocol_id': 'powermetrics_pulse_fiducial_v3'}}
triggers ['identity_field_change', 'protocol_or_estimator_byte_change', 'new_valid_same_identity_capture_expands_observed_range', 'corpus_doubles_from_19_to_38', 'new_systematic_failure_challenges_preflight_screen']
127:| D-102 | CAL-BRACKET-D079-01 pins: budget cap 0.001275166090593858 s (99% two-draw prediction ceiling 0.012093166090593858 s, blind n=19 derivation), exact-identity-epoch freshness with prospective re-derivation triggers, never-zero allowance max(drift, screen) embedded once, decimal-source numeric semantics with labelled presentation values | accepted (magistrate ratification, lead-replayed arithmetic, 2026-08-01) |
134:| D-109 | CAL-BRACKET-D079-01 F3: A-min-with-reservation — writer-enforced receipt ledger (reservation-first pending entry before capture, mandatory finalization, unresolved-pending refusal), ledger-only consumption, repo-committed head pin, single immutable snapshot threading; R1 authority/retention/anti-rollback (7 clauses) + R2 prior-observation set with the 38-total counting rule (8 clauses); Option B recorded as rejected fallback; lands with F1+F2 as the single combined fix round | accepted (Ed 2026-08-03, same deferral; Sol soundness breaks lead-verified and adopted) |
135:| D-110 | Mint #1 retroactively NON-CLAIM-BEARING (taint-and-remint, Ed ruling on sweep finding RT-1: floors embed zero allowance where D-102 pin 3 mandates +max(drift, 0.010818 s)); re-mint gated on D-109 landing + artifact issuance + validator pin widening; RT-2 dependency edge minted (MINT-GENERALIZE-01 hard-blocked on CAL-BRACKET-D079-01); night-consult 7B-mint license suspended; RT-5 recorded: all four PASSED window verdicts untainted | accepted (Ed 2026-08-03, sweep-triggered) |
141:| D-116 | D-079 calibration acceptance artifact ISSUED; ledger genesis import executed (seq 76 / head 08456d50…; issued sha 316113960c…; 30/2/6 dispositions); D-110 condition (b) SATISFIED → MINT-GENERALIZE-01 unblocked for re-mint; two-cold-gate history (plan HELD → consumer impl + gauntlet → bytes PROCEED, sequencing HOLD resolved by consumer-first merge); window_metrologyB calibration fiducials in completeness record are NOT a D-113 violation | executed (Fable magistrate, 2026-08-06; Ed pre-authorized) |
142:| D-117 | D-110's historical re-mint order SUPERSEDED (structurally unsatisfiable at main: issued ledger holds only import-marked receipts, candidate discovery excludes imports); replacement = THREE prospective claim windows (fresh 1.5B decode floor, fresh 7B decode floor, fresh decode contrast) live-bracketed under the issued regime; prefill floor cells ride the floor windows; contrast decode-only by default (≥256-token prefill arm stays Ed's open option); D-113 readiness rewired (three-window P1 closure precedes MET-WINDOW-C-01); Option 1 preserved as cold-gated contingency only | adopted (Ed directive, in-thread 2026-08-07; transcribed by the Fable magistrate) |
6280:## D-102: CAL-BRACKET-D079-01 pins ratified — corpus-derived budget cap, identity-epoch freshness, never-zero allowance, decimal numeric semantics
6988:## D-109: CAL-BRACKET-D079-01 F3 — A-min-with-reservation adopted (writer-enforced receipt ledger, reservation-first, repo-committed head pin); R1 ledger-authority and R2 prior-observation-set rulings
7005:  a faithful IMPLEMENTATION of D-102 (no threshold/freshness
7006:  amendment); it supplies the authority/universe rulings D-102 left
7070:   artifact (D-102's prospective rule).
7077:8. Counting rule for the D-102 corpus-doubling trigger (19→38): 38
7083:## D-110: Mint 1 retroactively NON-CLAIM-BEARING (taint-and-remint); RT-2 dependency edge minted; the night consult's 7B-mint license SUSPENDED
7085:> **2026-08-07 supersession (D-117):** clause 3's historical re-mint
7089:> allowance correction STAND and bind the D-117 mints.
7103:never-zero allowance of ZERO where D-102 pin 3 mandates
7111:D-102 epoch; the taint is confined to floor artifacts.
7118:2. RE-MINT CONDITIONS: (a) the D-109 CAL-BRACKET implementation lands
7160:   the D-108/D-109 debate record, the night-consult rulings memo, the
7209:## D-109 addendum II: reviewed mint-core interface amendment (integration-collision resolution); D-110 oracle clarification
7220:1. D-109 R1.4's `calibration_ledger_snapshot` threading is a DELIBERATE
7230:3. D-110 CLARIFICATION (conditions unchanged): tooling byte-identity
7233:   historical mint-1 digests — D-110's corrected re-mint may
7250:> **2026-08-07 amendment (D-117 cl.4):** the readiness dependency on
7251:> D-110's historical re-mint is REMOVED; the three-window P1 closure
7340:   artifact and the D-110 (b)+(c) re-mint chain; instrument/machine
7353:D-110 condition (c) is readiness assurance for Window C, not
7429:MINT-GENERALIZE-01 — whose D-110 condition (a) was satisfied the same
7489:## D-116: D-079 calibration acceptance artifact ISSUED; ledger genesis import executed (D-110 condition (b) SATISFIED)
7492:**Status:** EXECUTED. This retires the schema fixture and issues the authoritative calibration acceptance artifact — the anchor all future floor-mint claims authenticate against. D-110 re-mint condition (b) ("R2 backfill verified, ledger bootstrapped, head pinned") is now SATISFIED; (a) was satisfied by PR #100, (c) by PR #105. **MINT-GENERALIZE-01 is UNBLOCKED for the re-mint.**
7496:- `configs/calibration/calibration_ledger_head.json` — the repo-committed head pin (sequence 76, head_digest `08456d5076c18a9a7f758969b02f5b6f7ad9fcc267dd12e2d3778c22458094d7`), the D-109 R1.4 anti-rollback trust anchor.
7500:**Disposition inventory (B1 lead-ruled).** 30 valid / 2 systematic-invalid / 6 ordinary-invalid. The two systematic-invalid members (`20260726T000039-491995f3`, `20260801T064830-c76f5d1c`) have bounds `0.035435840879704805` / `0.0350400833260715`, both exceeding the ratified pre-flight screen `0.033558756679900`; D-102 (§~6298) explicitly names the first a systematic failure "never budgetable." R2.8 counting: 30 valid < 38 threshold, so issuance does NOT itself trigger corpus-doubling re-derivation (eight further valid same-epoch observations would; R2.8's literal "six further" was conditioned on the superseded 32-valid candidate). derivation_corpus preserved byte-identical at n=19 (its fixture whole-core digest was `3cece3b2…`; that value is NOT carried into the issued artifact — embedding it would fail the loader). All 38 custody locators are iCloud-backup copies (raw evidence is git-ignored by repo convention; integrity rests on the committed hash chain, not the custody pointer).
7502:**Window-B completeness note (soundness-critical, for any reviewer asking "why Window-B in the anchor?").** The `prior_observation_set` correctly includes 6 `window_metrologyB` **calibration fiducial** observations (2 valid: `e0ce33f5`, `8c3bfe9e`), as mandated by D-109 R2.3/R2.8 completeness (every content-distinct governed CALIBRATION observation). This is NOT a D-113 violation: D-113 retired Window B's WINDOW CLAIM consumption (its null-ladder/additivity science members), not the calibration fiducials collected in that period; the general calibration machinery survives per D-113. These fiducials are EXCLUDED from the frozen n=19 threshold basis (which is Window-A-only) and do not influence the bound.
7506:**Consequences.** MINT-GENERALIZE-01 (b) satisfied; the re-mint (a10 extraction + mint #1 re-derivation under the corrected selector, embedding the D-102 pin-3 never-zero drift allowance) is the next step — the path to a non-empty claims table. The runs/ ledger must be custody-backed before the re-mint consumes it.
7508:## D-117: D-110's historical re-mint order SUPERSEDED — prospective three-window replacement (Option 2) adopted; D-113 readiness rewired
7522:1. **The D-110 clause-3 re-mint order (historical a10 consumption under
7527:   inconvenient. D-110's OTHER holdings STAND untouched: mint #1 and
7529:   `A_s = max(observed_drift_s, 0.010818)` allowance (D-102 pin 3)
7559:   D-110 cl.1, logs sha-verified.
7567:   D-102 successor-artifact packet; results/methods prose placeholders.

exec
/bin/zsh -lc "sed -n '6280,6345p' docs/decision_log.md; sed -n '6988,7085p' docs/decision_log.md; sed -n '7489,7585p' docs/decision_log.md" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
## D-102: CAL-BRACKET-D079-01 pins ratified — corpus-derived budget cap, identity-epoch freshness, never-zero allowance, decimal numeric semantics

- Date: 2026-08-01
- Status: accepted (magistrate ratification after the two-round Sol xhigh
  design consult + the independent n=19 corpus reconstruction; ALL
  arithmetic lead-replayed at the bench: ceiling, cap, t(0.995,18)
  quantile by numerical CDF, window B pre-cal value against primary
  evidence bytes)
- Applies to: CAL-BRACKET-D079-01, the future
  `configs/calibration/calibration_acceptance_d079_v2.json` artifact

The four pins D-079 left unexecutable, now pinned:

1. **Budget cap (Candidate A, 99% two-draw prediction family, derived
   blind from the pre-window-B n=19 corpus):**
   `max_budgetable_excess_s = 0.001275166090593858`;
   `maximum_budgetable_drift_s = 0.012093166090593858`
   (= t(0.995,18)=2.878440472713585 × sd 0.002970761365307205 × √2;
   cap = ceiling − operative screen 0.010818). Consequences verified: a
   ~11.58 ms drift branch is budgetable; a 15 ms bracket refuses.
   **Window B itself remains refused regardless** — its pre-calibration
   0.035435840879704805 s (verified in primary evidence) exceeds the
   pre-flight level screen, and D-079 cl.2's systematic failure is
   never budgetable. The CAL-BRACKET regression at ~11 ms models the
   DRIFT BRANCH only, never a whole-window B pass.
2. **Freshness = exact identity epoch, no calendar hard expiry:** the
   artifact binds {os_build, hardware_model, power_policy,
   sampling_interval_ms, estimator_revision, pulse_protocol_id}; any
   change → `calibration_acceptance_bound_stale`. Mandatory prospective
   re-derivation triggers: any identity-field change; protocol/estimator
   byte change; a new valid same-identity calibration expanding the
   observed range; corpus doubling (19→38); a new systematic failure
   challenging the pre-flight screen. A trigger observation is judged
   under the PRIOR artifact — never incorporated into a threshold that
   judges itself. Calendar-age fields are provenance/advisory only (the
   corpus spans four days; a calendar constant would be invented).
3. **Never-zero allowance confirmed:**
   `A_s = max(observed_drift_s, 0.010818)`;
   `B_operative = max(B_pre, B_post) + A_s`, embedded ONCE in the
   authenticated operative fiducial bound (anchor-envelope
   re-reduction); no second calibration-drift energy term anywhere
   downstream (D-078 cl.11 single-count).
4. **Decimal numeric semantics:** the artifact stores source decimal
   lexemes and exact-decimal derivations (range
   0.010817749309353528 s; 95% prediction 0.008826584887500717 s;
   pre-flight exact max 0.03355875667989999 s) SEPARATELY from the
   ratified operative comparators (0.010818; 0.033558756679900;
   ROUND_HALF_EVEN at the declared quantum), hashing the decimal
   strings + rounding rule into the derivation sha256. D-079's
   12-place `0.010817749309` is a LABELLED presentation value, never a
   comparator. Acceptance comparisons run in decimal semantics;
   binary64 conversion happens only at the reducer boundary and is
   recorded.

Corpus provenance: the n=19 member list with per-member manifest and
evidence sha256s is reconstructed and lead-spot-verified (2026-08-01
session records; summary in the session custody dir) — the artifact
copies those tables verbatim with re-verification at authoring, never
retyped. Implementation remains sequenced behind gauntlet commit 3 and
the D-100 repair (shared write surfaces).

Revisit when: CAL-BRACKET-D079-01's delta audit reports, or any
re-derivation trigger fires.

## D-103: C3 structural cold-gate synthesis — WAL attestation ordering, two named aggregation policies (cold instance overruled on B2 with recorded dissent), reader-tolerant/writer-strict path discipline

## D-109: CAL-BRACKET-D079-01 F3 — A-min-with-reservation adopted (writer-enforced receipt ledger, reservation-first, repo-committed head pin); R1 ledger-authority and R2 prior-observation-set rulings

- Date: 2026-08-03
- Status: accepted (Ed ruling 2026-08-03: same explicit deferral to the
  joint magistrate + Sol position, same debate record. Arc: the fix
  investigation recommended A-min; Sol round 1 BROKE that formulation
  as stated (writer crash-window; prefix-subset is not anti-rollback)
  and recommended Option B for the timeline; magistrate round 2
  supplied the low-schedule-pressure record, the metrology-centric
  pivot, and the shared-R2 marginal-cost analysis; Sol WITHDREW B and
  converged on A-min-with-reservation, marginal cost Medium. Both
  soundness holes were lead-verified at the bench before adoption.)
- Applies to: `scripts/validate_powermetrics_fiducial.py` (sole
  production calibration writer), `joulewise/calibration_bracketing.py`,
  `joulewise/whole_window.py`, `scripts/run_campaign.py`,
  `configs/calibration/calibration_acceptance_d079_v2.json`, and every
  consumer construction of `AuthenticatedConsumptionSession`. This is
  a faithful IMPLEMENTATION of D-102 (no threshold/freshness
  amendment); it supplies the authority/universe rulings D-102 left
  silent. Lands with F1 + F2 as the single combined CAL-BRACKET fix
  round. Option B (signed narrowing amendment) is recorded as REJECTED
  fallback — coherent and honest, but it weakens the thesis instrument
  where the project has slack to build the sounder boundary.

**R1 — ledger authority, retention, anti-rollback (7 clauses):**
1. A canonical observation-receipt ledger and its append API are the
   SOLE authority for governed calibration observations. An off-ledger
   calibration artifact is invalid everywhere: as bracket endpoint,
   trigger evidence, derivation member, or claim evidence. Consumers
   enumerate ledger entries only, never caller-supplied directories.
2. RESERVATION-FIRST: every capture appends an authenticated `pending`
   attempt entry BEFORE hardware capture begins, and must finalize it
   as valid / systematic-invalid / ordinary-invalid / abandoned. Any
   unresolved pending, unfinalized, malformed, or conflicting entry
   causes claim evaluation to REFUSE. (Grounds, bench-verified: the
   writer creates capture state pre-receipt and has pre-manifest
   failure exits — a publish-on-return receipt misses exactly the
   crash/interrupt cases a completeness mechanism exists to catch.)
3. Receipts are immutable and hash-chained: sequence, predecessor,
   attempt id, content id, artifact hashes, six-field epoch, full T1,
   capture time, exact bound lexeme, disposition, custody locator.
4. The acceptance artifact pins its baseline ledger head. Evaluation
   ALSO requires the independent current-head pin (clause below),
   verifies one complete non-forked chain extension from baseline to
   current, and threads ONE immutable ledger snapshot through every
   consumer path (session, direct runner path, secondary verifier) —
   repeated independent loads are a refusal-grade defect.
   Anti-rollback authority: a REPO-COMMITTED head-pin file
   `{sequence, head_digest, ledger_schema}` (existing checked-in
   byte-pin trust model; no second trusted latest-sequence store).
   Rotation is epoch-bounded — at most one lead-controlled
   quiet-machine collection session — and NO claim evaluation may
   occur between ledger advancement and pin commit; a physical head
   differing from the committed pin refuses.
5. Ledger history is retained permanently. Referenced evidence remains
   in authenticated custody; missing or unverifiable required bytes
   cause refusal, never silent omission.
6. Version 1 is single-authority, single-machine. Remote/other-machine
   captures are invalid until imported through an authenticated ledger
   transaction; direct multi-machine append requires a new ruling.
7. Threat model, stated honestly and to be stated wherever A-min is
   described: the mechanism closes workflow omission, unregistered
   evidence, and rollback/stale-head consumption. It does NOT defend
   against a malicious trusted writer or an authority that rewrites
   both Git and ledger history. No stronger claim may be made.

**R2 — prior-observation set and prospective triggers (8 clauses):**
1. The issuance cutoff is an exact ledger sequence + head digest.
2. `derivation_corpus` remains exactly the n=19 threshold-producing
   observations.
3. `prior_observation_set` = every content-distinct governed
   observation known at the cutoff — valid, systematic-invalid,
   ordinary-invalid, blind holdout, and unresolved — with epoch and
   disposition recorded separately. (The current artifact's two
   ID-only `blind_exclusions` are insufficient and are superseded.)
4. Content identity is path-independent, derived from canonical
   primary-byte hashes; attempt identity is separate; copies do not
   create new observations.
5. "New" (trigger population) = current authentic content IDs −
   `prior_observation_set`, regardless of capture timestamp or source
   root; a previously unknown historical artifact IS new when
   discovered. Every new observation is judged under the PRIOR
   artifact (D-102's prospective rule).
6. New unresolved or unclassifiable attempts cause refusal; only after
   trigger disposition may a successor artifact absorb them.
7. The 32-valid/6-invalid same-epoch inventory is a backfill
   CANDIDATE, not a ratified classification: identities may seed the
   backfill, but dispositions require raw-physics + hash verification
   before issuance, and any unresolved member blocks issuance.
8. Counting rule for the D-102 corpus-doubling trigger (19→38): 38
   TOTAL authenticated, content-distinct, VALID same-epoch
   observations — including previously blind observations once
   unblinded — not 38 post-cutoff observations. Under the candidate
   inventory, six further valid observations trigger re-derivation.

## D-110: Mint 1 retroactively NON-CLAIM-BEARING (taint-and-remint); RT-2 dependency edge minted; the night consult's 7B-mint license SUSPENDED

> **2026-08-07 supersession (D-117):** clause 3's historical re-mint
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
/bin/zsh -lc "rg -n \"prepare_historical_import|generate_historical_custody_manifest|bootstrap_historical_import\" tests/test_calibration_ledger.py tests/test_calibration_bracketing.py; sed -n '1120,1510p' tests/test_calibration_ledger.py; sed -n '1080,1245p' joulewise/calibration_ledger.py" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
tests/test_calibration_bracketing.py:38:    bootstrap_historical_import,
tests/test_calibration_bracketing.py:632:            plan = bootstrap_historical_import(
tests/test_calibration_ledger.py:43:    bootstrap_historical_import,
tests/test_calibration_ledger.py:49:    generate_historical_custody_manifest,
tests/test_calibration_ledger.py:52:    prepare_historical_import,
tests/test_calibration_ledger.py:570:        plan = prepare_historical_import(
tests/test_calibration_ledger.py:761:        original = prepare_historical_import(
tests/test_calibration_ledger.py:773:        table_reformatted = prepare_historical_import(
tests/test_calibration_ledger.py:792:        manifest_reformatted = prepare_historical_import(
tests/test_calibration_ledger.py:826:        original = prepare_historical_import(
tests/test_calibration_ledger.py:838:        reformatted = prepare_historical_import(
tests/test_calibration_ledger.py:851:            bootstrap_historical_import(
tests/test_calibration_ledger.py:867:            prepare_historical_import(**import_args)
tests/test_calibration_ledger.py:882:            prepare_historical_import(**import_args)
tests/test_calibration_ledger.py:891:            bootstrap_historical_import(
tests/test_calibration_ledger.py:909:            bootstrap_historical_import(
tests/test_calibration_ledger.py:933:                bootstrap_historical_import(
tests/test_calibration_ledger.py:955:                bootstrap_historical_import(
tests/test_calibration_ledger.py:987:                bootstrap_historical_import(
tests/test_calibration_ledger.py:1004:            confirmed = bootstrap_historical_import(
tests/test_calibration_ledger.py:1019:            bootstrap_historical_import(
tests/test_calibration_ledger.py:1034:        plan = prepare_historical_import(
tests/test_calibration_ledger.py:1100:                "prepare_historical_import",
tests/test_calibration_ledger.py:1110:                "bootstrap_historical_import",
tests/test_calibration_ledger.py:1151:        plan = prepare_historical_import(
tests/test_calibration_ledger.py:1157:                bootstrap_historical_import(
tests/test_calibration_ledger.py:1200:                    bootstrap_historical_import(
tests/test_calibration_ledger.py:1272:            bootstrap_historical_import(
tests/test_calibration_ledger.py:1307:module.bootstrap_historical_import(
tests/test_calibration_ledger.py:1323:        plan = bootstrap_historical_import(
tests/test_calibration_ledger.py:1356:                bootstrap_historical_import(
tests/test_calibration_ledger.py:1372:        plan = bootstrap_historical_import(
tests/test_calibration_ledger.py:1429:        manifest = generate_historical_custody_manifest(
tests/test_calibration_ledger.py:1444:        plan = prepare_historical_import(
tests/test_calibration_ledger.py:1462:            prepare_historical_import(
tests/test_calibration_ledger.py:1467:        manifest_only = prepare_historical_import(**import_args)
tests/test_calibration_ledger.py:1476:            prepare_historical_import(
tests/test_calibration_ledger.py:1524:            plan = prepare_historical_import(
        ):
            exit_code = bootstrap_cli.main()
        serialize.assert_not_called()
        self.assertEqual(exit_code, bootstrap_cli.DURABILITY_UNCERTAIN_EXIT)
        self.assertNotEqual(exit_code, 2)
        rows = [json.loads(line) for line in stdout.buffer.getvalue().splitlines()]
        self.assertEqual(len(rows), len(plan.receipts) + 2)
        self.assertEqual(rows[-2]["record"], "issued-acceptance-artifact")
        self.assertEqual(rows[-1]["record"], "bootstrap-summary")
        self.assertTrue(rows[-1]["executed"])
        self.assertEqual(
            rows[-1]["outcome"], "committed_durability_uncertain"
        )
        self.assertEqual(rows[-1]["head_digest"], plan.head_digest)
        self.assertEqual(
            rows[-1]["disposition_table_sha256"],
            plan.disposition_table_sha256,
        )
        self.assertEqual(
            rows[-1]["custody_manifest_sha256"],
            plan.custody_manifest_sha256,
        )
        self.assertEqual(
            rows[-1]["issued_artifact_file_sha256"], issued_file_sha256
        )
        self.assertEqual(emitted_path.read_bytes(), issued_raw)
        self.assertIn("rerun the identical --execute invocation", stderr.getvalue())

    def test_tampered_nonempty_ledger_never_enters_confirm_path(self) -> None:
        checkout, root, custodies, table = self._historical_fixture()
        import_args = self._historical_import_args(table, custodies)
        plan = prepare_historical_import(
            roots=[root], checkout_root=checkout, **import_args
        )
        self.ledger.write_bytes(plan.ledger_bytes + b"tampered\n")
        with mock.patch.object(calibration_ledger, "_fsync_parent_directory") as sync:
            with self.assertRaisesRegex(CalibrationLedgerError, "empty ledger"):
                bootstrap_historical_import(
                    self.ledger,
                    head_pin_path=self.pin,
                    roots=[root],
                    checkout_root=checkout,
                    **import_args,
                    execute=True,
                    require_committed_pin=False,
                )
        sync.assert_not_called()
        self.assertEqual(self.ledger.read_bytes(), plan.ledger_bytes + b"tampered\n")

    def test_stable_lock_serializes_replace_against_waiting_old_writer(
        self,
    ) -> None:
        checkout, root, custodies, table = self._historical_fixture()
        import_args = self._historical_import_args(table, custodies)
        self.ledger.write_bytes(b"")
        lock_path = calibration_ledger._ledger_lock_path(self.ledger)
        bootstrap_locked = threading.Event()
        allow_replace = threading.Event()
        writer_waiting = threading.Event()
        real_reauthenticate = calibration_ledger._reauthenticate_historical_import_plan
        real_flock = calibration_ledger.fcntl.flock
        bootstrap_results = []
        bootstrap_errors = []
        writer_results = []
        writer_errors = []

        def pause_with_bootstrap_lock(plan):
            bootstrap_locked.set()
            if not allow_replace.wait(timeout=5):
                raise RuntimeError("test timed out before replace release")
            real_reauthenticate(plan)

        def observe_writer_lock(descriptor, operation):
            if threading.current_thread().name == "stale-ledger-writer":
                writer_waiting.set()
            return real_flock(descriptor, operation)

        def run_bootstrap():
            try:
                bootstrap_results.append(
                    bootstrap_historical_import(
                        self.ledger,
                        head_pin_path=self.pin,
                        roots=[root],
                        checkout_root=checkout,
                        **import_args,
                        execute=True,
                        require_committed_pin=False,
                    )
                )
            except Exception as exc:  # pragma: no cover - asserted below
                bootstrap_errors.append(exc)

        def run_writer():
            try:
                writer_results.append(self._reserve("stale-writer", self.root / "x"))
            except Exception as exc:
                writer_errors.append(exc)

        with (
            mock.patch.object(
                calibration_ledger,
                "_reauthenticate_historical_import_plan",
                side_effect=pause_with_bootstrap_lock,
            ),
            mock.patch.object(
                calibration_ledger.fcntl,
                "flock",
                side_effect=observe_writer_lock,
            ),
        ):
            bootstrap_thread = threading.Thread(target=run_bootstrap)
            bootstrap_thread.start()
            self.assertTrue(bootstrap_locked.wait(timeout=5))
            lock_inode_before = lock_path.stat().st_ino
            writer_thread = threading.Thread(
                target=run_writer, name="stale-ledger-writer"
            )
            writer_thread.start()
            self.assertTrue(writer_waiting.wait(timeout=5))
            allow_replace.set()
            bootstrap_thread.join(timeout=5)
            writer_thread.join(timeout=5)
        self.assertFalse(bootstrap_thread.is_alive())
        self.assertFalse(writer_thread.is_alive())
        self.assertEqual(bootstrap_errors, [])
        self.assertEqual(len(bootstrap_results), 1)
        self.assertEqual(writer_results, [])
        self.assertEqual(len(writer_errors), 1)
        self.assertIn("head differs", str(writer_errors[0]))
        self.assertEqual(
            self.ledger.read_bytes(), bootstrap_results[0].ledger_bytes
        )
        self.assertTrue(lock_path.exists())
        self.assertEqual(lock_path.stat().st_ino, lock_inode_before)

    def test_hostile_lock_identity_refuses_and_ordinary_lockfile_proceeds(
        self,
    ) -> None:
        self.ledger.write_bytes(b"")
        lock_path = calibration_ledger._ledger_lock_path(self.ledger)

        lock_path.symlink_to(self.ledger)
        with self.assertRaisesRegex(CalibrationLedgerError, "opened safely"):
            self._reserve("symlink-lock", self.root / "symlink-lock-custody")
        lock_path.unlink()

        os_link = getattr(calibration_ledger.os, "link")
        os_link(self.ledger, lock_path)
        checkout, root, custodies, table = self._historical_fixture()
        import_args = self._historical_import_args(table, custodies)
        with self.assertRaisesRegex(CalibrationLedgerError, "dedicated regular"):
            bootstrap_historical_import(
                self.ledger,
                head_pin_path=self.pin,
                roots=[root],
                checkout_root=checkout,
                **import_args,
                execute=True,
                require_committed_pin=False,
            )
        lock_path.unlink()

        receipt = self._reserve("ordinary-lock", self.root / "ordinary-custody")
        lock_status = lock_path.stat()
        ledger_status = self.ledger.stat()
        self.assertEqual(receipt["event"], "reservation")
        self.assertTrue(stat.S_ISREG(lock_status.st_mode))
        self.assertEqual(lock_status.st_nlink, 1)
        self.assertNotEqual(
            (lock_status.st_dev, lock_status.st_ino),
            (ledger_status.st_dev, ledger_status.st_ino),
        )

    def test_sigkill_mid_import_leaves_retryable_genesis(self) -> None:
        checkout, root, custodies, table = self._historical_fixture()
        import_args = self._historical_import_args(table, custodies)
        code = f"""
import os, signal
from pathlib import Path
import joulewise.calibration_ledger as module
def die_mid_write(handle, payload):
    handle.write(payload[:len(payload) // 2])
    handle.flush()
    os.fsync(handle.fileno())
    os.kill(os.getpid(), signal.SIGKILL)
module._write_bootstrap_payload = die_mid_write
module.bootstrap_historical_import(
    Path({str(self.ledger)!r}),
    head_pin_path=Path({str(self.pin)!r}),
    roots=[Path({str(root)!r})],
    checkout_root=Path({str(checkout)!r}),
    disposition_table_raw={import_args['disposition_table_raw']!r},
    expected_disposition_table_sha256={import_args['expected_disposition_table_sha256']!r},
    custody_manifest_raw={import_args['custody_manifest_raw']!r},
    expected_custody_manifest_sha256={import_args['expected_custody_manifest_sha256']!r},
    execute=True,
    require_committed_pin=False,
)
"""
        killed = subprocess.run([sys.executable, "-c", code], check=False)
        self.assertEqual(killed.returncode, -signal.SIGKILL)
        self.assertEqual(self.ledger.read_bytes(), b"")
        plan = bootstrap_historical_import(
            self.ledger,
            head_pin_path=self.pin,
            roots=[root],
            checkout_root=checkout,
            **import_args,
            execute=True,
            require_committed_pin=False,
        )
        self.assertEqual(self.ledger.read_bytes(), plan.ledger_bytes)

    def test_execute_reauthenticates_all_artifacts_after_lock(self) -> None:
        checkout, root, custodies, table = self._historical_fixture()
        import_args = self._historical_import_args(table, custodies)
        original_gate = calibration_ledger._require_genesis_bootstrap_state
        calls = 0

        def mutate_after_locked_gate(*args, **kwargs):
            nonlocal calls
            calls += 1
            original_gate(*args, **kwargs)
            if calls == 2:
                with (custodies[0] / "events.jsonl").open("ab") as handle:
                    handle.write(b"drift-after-prepare\n")

        with mock.patch.object(
            calibration_ledger,
            "_require_genesis_bootstrap_state",
            side_effect=mutate_after_locked_gate,
        ):
            with self.assertRaisesRegex(
                CalibrationLedgerError, "reauthentication failed"
            ):
                bootstrap_historical_import(
                    self.ledger,
                    head_pin_path=self.pin,
                    roots=[root],
                    checkout_root=checkout,
                    **import_args,
                    execute=True,
                    require_committed_pin=False,
                )
        self.assertEqual(self.ledger.read_bytes(), b"")

    def test_historical_import_marker_is_not_a_post_cutoff_live_observation(
        self,
    ) -> None:
        checkout, root, custodies, table = self._historical_fixture()
        import_args = self._historical_import_args(table, custodies)
        plan = bootstrap_historical_import(
            self.ledger,
            head_pin_path=self.pin,
            roots=[root],
            checkout_root=checkout,
            **import_args,
            execute=True,
            require_committed_pin=False,
        )
        self._write_pin(dict(plan.head_pin))
        snapshot = load_calibration_ledger_snapshot(
            self.ledger,
            self.pin,
            require_committed_pin=False,
            repo_root=checkout,
        )
        self.assertTrue(snapshot.valid)
        self.assertEqual(len(snapshot.observations), 3)
        self.assertTrue(all(row.is_historical_import for row in snapshot.observations))
        self.assertEqual(snapshot.post_cutoff_live_observations(0), ())
        self.assertEqual(
            {receipt["event"] for receipt in snapshot.receipts},
            {
                HISTORICAL_IMPORT_RESERVATION_EVENT,
                HISTORICAL_IMPORT_FINALIZATION_EVENT,
            },
        )

    def test_live_capture_finalization_cannot_carry_import_marker(self) -> None:
        custody = self._custody("live-marker-boundary")
        self._reserve("live-marker-boundary", custody)
        final = self._finalize("live-marker-boundary", custody)
        self._write_pin(head_pin_for_receipt(final))
        snapshot = self._snapshot()
        self.assertTrue(snapshot.valid)
        self.assertEqual(len(snapshot.observations), 1)
        self.assertFalse(snapshot.observations[0].is_historical_import)
        self.assertEqual(
            {receipt["event"] for receipt in snapshot.receipts},
            {"reservation", "finalization"},
        )

    def test_historical_import_manifest_pins_head_and_subset_roots_refuse(
        self,
    ) -> None:
        checkout, root, custodies, table = self._historical_fixture()
        source = custodies[0]
        duplicate = (
            checkout
            / "a_duplicate"
            / "instrument_validation"
            / source.name
        )
        duplicate.parent.mkdir(parents=True)
        shutil.copytree(source, duplicate)
        table_raw = (json.dumps(table, indent=2, sort_keys=True) + "\n").encode()
        table_sha = hashlib.sha256(table_raw).hexdigest()
        manifest = generate_historical_custody_manifest(
            roots=[root, checkout / "a_duplicate"],
            checkout_root=checkout,
            disposition_table_raw=table_raw,
            expected_disposition_table_sha256=table_sha,
        )
        manifest_raw = custody_manifest_bytes(manifest)
        import_args = {
            "disposition_table_raw": table_raw,
            "expected_disposition_table_sha256": table_sha,
            "custody_manifest_raw": manifest_raw,
            "expected_custody_manifest_sha256": hashlib.sha256(
                manifest_raw
            ).hexdigest(),
        }
        plan = prepare_historical_import(
            roots=[root, checkout / "a_duplicate"],
            checkout_root=checkout,
            **import_args,
        )
        imported = next(
            row
            for row in plan.receipts
            if row["attempt_id"] == source.name
            and row["event"] == HISTORICAL_IMPORT_FINALIZATION_EVENT
        )
        self.assertEqual(
            imported["custody_locator"],
            str(duplicate.resolve()),
        )
        with self.assertRaisesRegex(
            CalibrationLedgerError, "absent from root discovery"
        ):
            prepare_historical_import(
                roots=[root],
                checkout_root=checkout,
                **import_args,
            )
        manifest_only = prepare_historical_import(**import_args)
        self.assertEqual(manifest_only.head_digest, plan.head_digest)

    def test_historical_import_refuses_tampered_evidence_bytes(self) -> None:
        checkout, root, custodies, table = self._historical_fixture()
        import_args = self._historical_import_args(table, custodies)
        with (custodies[1] / "events.jsonl").open("ab") as handle:
            handle.write(b"tampered\n")
        with self.assertRaisesRegex(CalibrationLedgerError, "hash mismatch"):
            prepare_historical_import(
                roots=[root],
                checkout_root=checkout,
                **import_args,
            )

    def test_three_member_historical_import_has_hand_computed_head(self) -> None:
        checkout, root, custodies, table = self._historical_fixture()
        import_args = self._historical_import_args(table, custodies)
        inspect_candidate = calibration_ledger._inspect_historical_candidate

        manifest = json.loads(import_args["custody_manifest_raw"])
        manifest["members"] = {
            content_id: (
                "/fixture-checkout/"
                f"{Path(locator).relative_to(checkout.resolve())}"
            )
            for content_id, locator in manifest["members"].items()
        }
        manifest_raw = custody_manifest_bytes(manifest)
        import_args["custody_manifest_raw"] = manifest_raw
        import_args["expected_custody_manifest_sha256"] = hashlib.sha256(
            manifest_raw
        ).hexdigest()

        def stable_vector_candidate(locator, *args, **kwargs):
            actual = checkout.resolve() / Path(locator).relative_to(
                "/fixture-checkout"
            )
            content_id, candidate, error = inspect_candidate(
                actual, *args, **kwargs
            )
            if candidate is not None:
                candidate = replace(
                    candidate,
        )
    ):
        return content_id, None, f"{directory}: manifest artifact hash mismatch"
    if (
        not isinstance(evidence_artifacts, Mapping)
        or set(evidence_artifacts) != set(EVIDENCE_BOUND_ARTIFACTS)
        or any(
            evidence_artifacts.get(name) != hashes[name]
            for name in EVIDENCE_BOUND_ARTIFACTS
        )
    ):
        return content_id, None, f"{directory}: evidence artifact hash mismatch"

    attempt_id = evidence.get("validation_id")
    if (
        not isinstance(attempt_id, str)
        or not attempt_id
        or manifest.get("validation_id") != attempt_id
    ):
        return content_id, None, f"{directory}: attempt identity mismatch"
    t1_bindings = _normalized_vector(bindings, T1_FIELDS)
    if any(t1_bindings.get(field) in (None, "") for field in T1_FIELDS):
        return content_id, None, f"{directory}: full T1 binding is incomplete"
    try:
        lexemes = _number_lexemes(evidence_raw, evidence_path)
    except CalibrationLedgerError as exc:
        return content_id, None, str(exc)
    capture = lexemes.get("capture_wall_time_s")
    bound = lexemes.get("b_fiducial_s")
    if capture is not None and not isinstance(capture, str):
        return content_id, None, f"{directory}: capture time lexeme is invalid"
    if bound is not None and not isinstance(bound, str):
        return content_id, None, f"{directory}: bound lexeme is invalid"
    if capture is None:
        return content_id, None, f"{directory}: capture time is missing"
    return (
        content_id,
        _HistoricalCandidate(
            attempt_id=attempt_id,
            content_id=content_id,
            artifact_sha256=MappingProxyType(hashes),
            identity_epoch=MappingProxyType(epoch),
            t1_bindings=MappingProxyType(t1_bindings),
            capture_wall_time_s=capture,
            exact_bound_lexeme_s=bound,
            custody_sort_key=custody_sort_key,
            custody_locator=resolved.as_posix(),
        ),
        None,
    )


def _discover_historical_candidates(
    *,
    roots: Sequence[Path],
    checkout_root: Path,
    expected_epoch: Mapping[str, Any],
) -> tuple[dict[str, list[_HistoricalCandidate]], dict[str, list[str]]]:
    try:
        checkout = Path(checkout_root).resolve(strict=True)
    except OSError as exc:
        raise CalibrationLedgerError("checkout root is unreadable") from exc

    complete: dict[str, list[_HistoricalCandidate]] = {}
    incomplete: dict[str, list[str]] = {}
    unknown_errors: list[str] = []
    for directory in _historical_directories(roots):
        content_id, candidate, error = _inspect_historical_candidate(
            directory,
            checkout_root=checkout,
            expected_epoch=expected_epoch,
        )
        if candidate is not None:
            complete.setdefault(candidate.content_id, []).append(candidate)
        elif error is not None:
            if content_id is None:
                unknown_errors.append(error)
            else:
                incomplete.setdefault(content_id, []).append(error)
    if unknown_errors:
        raise CalibrationLedgerError(sorted(unknown_errors)[0])

    return complete, incomplete


def generate_historical_custody_manifest(
    *,
    roots: Sequence[Path],
    checkout_root: Path,
    disposition_table_raw: bytes,
    expected_disposition_table_sha256: str,
) -> Mapping[str, Any]:
    """Apply the lexicographic selection rule for a lead-reviewed manifest."""

    table = _authenticated_json_object(
        disposition_table_raw,
        expected_disposition_table_sha256,
        label="disposition table",
    )
    expected_epoch, table_by_content = _historical_import_table(table)
    complete, incomplete = _discover_historical_candidates(
        roots=roots,
        checkout_root=checkout_root,
        expected_epoch=expected_epoch,
    )
    expected_ids = set(table_by_content)
    extra_ids = sorted((set(complete) | set(incomplete)) - expected_ids)
    missing_ids = sorted(expected_ids - set(complete))
    if extra_ids:
        raise CalibrationLedgerError(
            f"historical import table omits authenticated content_id {extra_ids[0]}"
        )
    if missing_ids:
        detail = sorted(incomplete.get(missing_ids[0], []))
        if detail:
            raise CalibrationLedgerError(detail[0])
        raise CalibrationLedgerError(
            f"historical import content_id is missing: {missing_ids[0]}"
        )
    members: dict[str, str] = {}
    for content_id in sorted(expected_ids):
        candidate = min(
            complete[content_id], key=lambda item: item.custody_sort_key
        )
        member = table_by_content[content_id]
        if candidate.attempt_id != member["attempt_id"]:
            raise CalibrationLedgerError(
                f"{content_id}: attempt_id differs from disposition table"
            )
        if dict(candidate.artifact_sha256) != dict(member["artifact_sha256"]):
            raise CalibrationLedgerError(
                f"{content_id}: artifact hashes differ from disposition table"
            )
        members[content_id] = candidate.custody_locator
    return {
        "schema_version": HISTORICAL_IMPORT_CUSTODY_MANIFEST_SCHEMA,
        "ledger_schema": LEDGER_SCHEMA,
        "members": members,
    }


def prepare_historical_import(
    *,
    roots: Sequence[Path] = (),
    checkout_root: Path = REPO_ROOT,
    disposition_table_raw: bytes,
    expected_disposition_table_sha256: str,
    custody_manifest_raw: bytes,
    expected_custody_manifest_sha256: str,
) -> HistoricalImportPlan:
    """Authenticate reviewed inputs and prepare the canonical genesis chain."""

    disposition_table = _authenticated_json_object(
        disposition_table_raw,
        expected_disposition_table_sha256,
        label="disposition table",
    )
    expected_epoch, table_by_content = _historical_import_table(disposition_table)
    custody_manifest = _authenticated_json_object(
        custody_manifest_raw,
        expected_custody_manifest_sha256,
        label="custody manifest",
    )
    pinned = _historical_import_custody_manifest(
        custody_manifest,
        expected_content_ids=set(table_by_content),

exec
/bin/zsh -lc "rg -n \"def _historical_fixture|def _historical_import_args|def _write_historical\" tests/test_calibration_ledger.py; sed -n '280,590p' tests/test_calibration_ledger.py" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
252:    def _historical_fixture(self):
288:    def _historical_import_args(self, table: dict, custodies: list[Path]) -> dict:
        table = {
            "schema_version": HISTORICAL_IMPORT_TABLE_SCHEMA,
            "ledger_schema": LEDGER_SCHEMA,
            "identity_epoch": dict(self.epoch),
            "members": members,
        }
        return checkout, checkout / "runs_fixture", custodies, table

    def _historical_import_args(self, table: dict, custodies: list[Path]) -> dict:
        table_raw = (json.dumps(table, indent=2, sort_keys=True) + "\n").encode()
        manifest = {
            "schema_version": HISTORICAL_IMPORT_CUSTODY_MANIFEST_SCHEMA,
            "ledger_schema": LEDGER_SCHEMA,
            "members": {
                member["content_id"]: str(custody.resolve())
                for member, custody in zip(table["members"], custodies)
            },
        }
        manifest_raw = custody_manifest_bytes(manifest)
        return {
            "disposition_table_raw": table_raw,
            "expected_disposition_table_sha256": hashlib.sha256(
                table_raw
            ).hexdigest(),
            "custody_manifest_raw": manifest_raw,
            "expected_custody_manifest_sha256": hashlib.sha256(
                manifest_raw
            ).hexdigest(),
        }

    def test_crash_between_reservation_and_finalization_refuses(self) -> None:
        custody = self.root / "never-created"
        pending = self._reserve("crash-attempt", custody)
        self._write_pin(head_pin_for_receipt(pending))
        snapshot = self._snapshot()
        self.assertIn("calibration_ledger_pending", snapshot.refusal_reasons)
        self.assertFalse(custody.exists())

    def test_reservation_requires_complete_epoch_and_full_t1(self) -> None:
        with self.assertRaisesRegex(
            CalibrationLedgerError, "malformed receipt"
        ):
            append_pending_receipt(
                self.ledger,
                attempt_id="partial-reservation",
                custody_locator=str(self.root / "partial"),
                identity_epoch={"power_policy": "ac_high_power"},
                t1_bindings={"power_policy": "ac_high_power"},
                head_pin_path=self.pin,
                require_committed_pin=False,
            )

    def test_production_writer_reserves_before_capture_state_or_sampler(self) -> None:
        source = (
            Path(__file__).resolve().parents[1]
            / "scripts"
            / "validate_powermetrics_fiducial.py"
        ).read_text(encoding="utf-8")
        reservation = source.index("\n    append_pending_receipt(")
        directory_creation = source.index('(out_dir / "raw").mkdir')
        sampler_launch = source.index("process = subprocess.Popen(")
        uncaught_finalizer = source.index("atexit.register(finalize_abandoned)")

        self.assertLess(reservation, directory_creation)
        self.assertLess(reservation, sampler_launch)
        self.assertLess(uncaught_finalizer, directory_creation)

    def test_proper_prefix_of_pinned_head_refuses_as_rollback(self) -> None:
        custody = self._custody("rollback")
        self._reserve("rollback", custody)
        final = self._finalize("rollback", custody)
        self._write_pin(head_pin_for_receipt(final))
        lines = self.ledger.read_bytes().splitlines(keepends=True)
        self.ledger.write_bytes(lines[0])
        snapshot = self._snapshot(verify_custody=False)
        self.assertIn("calibration_ledger_rollback", snapshot.refusal_reasons)

    def test_unpinned_physical_extension_refuses_stale_head(self) -> None:
        custody = self._custody("uncommitted")
        self._reserve("uncommitted", custody)
        snapshot = self._snapshot(verify_custody=False)
        self.assertIn("calibration_ledger_head_mismatch", snapshot.refusal_reasons)

    def test_true_sibling_fork_refuses_on_predecessor_conflict(self) -> None:
        custody = self._custody("fork")
        first = self._reserve("fork", custody)
        final = self._finalize("fork", custody)
        sibling = {
            **dict(first),
            "sequence": 3,
            "predecessor_digest": first["receipt_digest"],
            "attempt_id": "fork-sibling",
            "custody_locator": str(self.root / "fork-sibling"),
        }
        sibling["receipt_digest"] = canonical_sha256(
            {key: value for key, value in sibling.items() if key != "receipt_digest"}
        )
        with self.ledger.open("ab") as handle:
            handle.write(canonical_json_bytes(sibling) + b"\n")
        self._write_pin(head_pin_for_receipt(sibling))
        snapshot = self._snapshot(verify_custody=False)
        self.assertIn("calibration_ledger_chain_conflict", snapshot.refusal_reasons)
        self.assertNotIn(
            "calibration_ledger_attempt_conflict", snapshot.refusal_reasons
        )
        self.assertNotIn("calibration_ledger_head_mismatch", snapshot.refusal_reasons)
        self.assertEqual(sibling["receipt_digest"], snapshot.head_digest)
        self.assertNotEqual(final["receipt_digest"], sibling["receipt_digest"])

    def test_content_bearing_abandoned_receipt_is_unresolved_evidence(self) -> None:
        custody = self._custody("abandoned-content")
        self._reserve("abandoned-content", custody)
        final = self._finalize(
            "abandoned-content", custody, disposition="abandoned"
        )
        self._write_pin(head_pin_for_receipt(final))
        snapshot = self._snapshot()
        observation = snapshot.observation_by_attempt["abandoned-content"]
        self.assertIsNotNone(observation.content_id)
        self.assertEqual(observation.disposition, "abandoned")
        self.assertEqual(observation.classification_disposition, "unresolved")

    def test_finalization_is_single_transition(self) -> None:
        custody = self._custody("single")
        self._reserve("single", custody)
        self._finalize("single", custody)
        with self.assertRaisesRegex(CalibrationLedgerError, "uniquely pending"):
            self._finalize("single", custody)

    def test_missing_or_changed_custody_bytes_refuse(self) -> None:
        custody = self._custody("custody")
        self._reserve("custody", custody)
        final = self._finalize("custody", custody)
        self._write_pin(head_pin_for_receipt(final))
        (custody / "instrument_evidence.json").write_text("changed\n")
        snapshot = self._snapshot()
        self.assertEqual(
            snapshot.refusal_reasons,
            ("calibration_ledger_custody_invalid",),
        )

    def test_baseline_must_be_exact_member_of_current_chain(self) -> None:
        snapshot = load_calibration_ledger_snapshot(
            self.ledger,
            self.pin,
            baseline_sequence=1,
            baseline_digest="f" * 64,
            require_committed_pin=False,
        )
        self.assertIn("calibration_ledger_baseline_missing", snapshot.refusal_reasons)

    def test_historical_import_cli_dry_run_is_byte_stable_and_writes_nothing(
        self,
    ) -> None:
        checkout, root, custodies, table = self._historical_fixture()
        import_args = self._historical_import_args(table, custodies)
        table_path = self.root / "dispositions.json"
        table_path.write_text(
            json.dumps(table, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        manifest_path = self.root / "custody-manifest.json"
        manifest_path.write_bytes(import_args["custody_manifest_raw"])
        dry_ledger = self.root / "dry-run-ledger.jsonl"
        script, head_pin = self._isolated_cli_checkout()
        command = [
            sys.executable,
            str(script),
            "--disposition-table",
            str(table_path),
            "--expected-table-sha256",
            import_args["expected_disposition_table_sha256"],
            "--custody-manifest",
            str(manifest_path),
            "--expected-custody-manifest-sha256",
            import_args["expected_custody_manifest_sha256"],
            "--checkout-root",
            str(checkout),
            "--ledger",
            str(dry_ledger),
            "--head-pin",
            str(head_pin),
            str(root),
        ]
        first = subprocess.run(command, check=True, capture_output=True)
        second = subprocess.run(command, check=True, capture_output=True)
        self.assertEqual(first.stdout, second.stdout)
        self.assertEqual(first.stderr, b"")
        self.assertFalse(dry_ledger.exists())
        rows = [json.loads(line) for line in first.stdout.splitlines()]
        self.assertEqual(len(rows), 7)
        self.assertEqual(rows[-1]["record"], "bootstrap-summary")
        self.assertFalse(rows[-1]["executed"])
        self.assertEqual(rows[-1]["outcome"], "planned")
        self.assertEqual(rows[-1]["final_sequence"], 6)
        self.assertEqual(
            rows[-1]["disposition_table_sha256"],
            import_args["expected_disposition_table_sha256"],
        )
        self.assertEqual(
            rows[-1]["custody_manifest_sha256"],
            import_args["expected_custody_manifest_sha256"],
        )
        wrong_digest = list(command)
        digest_index = wrong_digest.index("--expected-table-sha256") + 1
        wrong_digest[digest_index] = "0" * 64
        refused = subprocess.run(wrong_digest, check=False, capture_output=True)
        self.assertEqual(refused.returncode, 2)
        self.assertIn(b"disposition table sha256 mismatch", refused.stderr)
        emitted = subprocess.run(
            [
                sys.executable,
                str(script),
                "--disposition-table",
                str(table_path),
                "--expected-table-sha256",
                import_args["expected_disposition_table_sha256"],
                "--checkout-root",
                str(checkout),
                "--emit-custody-manifest",
                str(root),
            ],
            check=True,
            capture_output=True,
        )
        self.assertEqual(emitted.stdout, import_args["custody_manifest_raw"])
        self.assertIn(
            import_args["expected_custody_manifest_sha256"].encode(),
            emitted.stderr,
        )
        self.assertFalse(dry_ledger.exists())

    @unittest.skipUnless(
        _REAL_D079_TABLE.is_file() and _REAL_D079_CUSTODY_MANIFEST.is_file(),
        "lead-reviewed D-079 import inputs are unavailable",
    )
    def test_d079_issued_artifact_mode_is_deterministic_and_write_explicit(
        self,
    ) -> None:
        script, head_pin = self._isolated_cli_checkout()
        dry_ledger = self.root / "issued-mode-ledger.jsonl"
        emitted_path = self.root / "issued-acceptance.json"
        source_path = self.root / "unissued-acceptance.json"
        source_raw = _unissued_acceptance_fixture_bytes()
        source_path.write_bytes(source_raw)
        command = [
            sys.executable,
            str(script),
            "--disposition-table",
            str(_REAL_D079_TABLE),
            "--expected-table-sha256",
            _REAL_D079_TABLE_SHA256,
            "--custody-manifest",
            str(_REAL_D079_CUSTODY_MANIFEST),
            "--expected-custody-manifest-sha256",
            _REAL_D079_CUSTODY_MANIFEST_SHA256,
            "--checkout-root",
            "/Users/edr",
            "--ledger",
            str(dry_ledger),
            "--head-pin",
            str(head_pin),
            "--acceptance-artifact",
            str(source_path),
            "--prepare-issued-artifact",
        ]
        first = subprocess.run(command, check=True, capture_output=True)
        self.assertEqual(first.stderr, b"")
        self.assertFalse(dry_ledger.exists())
        self.assertFalse(emitted_path.exists())
        rows = [json.loads(line) for line in first.stdout.splitlines()]
        issued = next(
            row for row in rows if row["record"] == "issued-acceptance-artifact"
        )
        summary = rows[-1]
        self.assertEqual(summary["record"], "bootstrap-summary")
        self.assertEqual(summary["final_sequence"], 76)
        self.assertEqual(
            summary["head_digest"],
            "08456d5076c18a9a7f758969b02f5b6f7ad9fcc267dd12e2d3778c22458094d7",
        )
        self.assertEqual(
            issued["derivation_sha256"], _ISSUED_D079_DERIVATION_SHA256
        )
        self.assertEqual(issued["artifact_file_sha256"], _ISSUED_D079_FILE_SHA256)
        self.assertEqual(
            len(issued["artifact"]["prior_observation_set"]["observations"]),
            38,
        )
        self.assertEqual(issued["artifact"]["derivation_corpus"]["n"], 19)

        plan = prepare_historical_import(
            checkout_root=Path("/Users/edr"),
            disposition_table_raw=_REAL_D079_TABLE.read_bytes(),
            expected_disposition_table_sha256=_REAL_D079_TABLE_SHA256,
            custody_manifest_raw=_REAL_D079_CUSTODY_MANIFEST.read_bytes(),
            expected_custody_manifest_sha256=(
                _REAL_D079_CUSTODY_MANIFEST_SHA256
            ),
        )
        source = _unissued_acceptance_fixture()
        reversed_source = dict(reversed(tuple(source.items())))
        canonical_artifact = bootstrap_cli._issued_acceptance_artifact(
            plan, source, source_artifact_raw=source_raw
        )
        reordered_artifact = bootstrap_cli._issued_acceptance_artifact(
            plan, reversed_source, source_artifact_raw=source_raw
        )
        canonical_bytes = bootstrap_cli._issued_artifact_bytes(
            canonical_artifact
        )
        reordered_bytes = bootstrap_cli._issued_artifact_bytes(

exec
/bin/zsh -lc "sed -n '235,305p' tests/test_calibration_ledger.py" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
        ).encode()
        (custody / "instrument_evidence.json").write_bytes(evidence_raw)
        manifest_artifacts = {
            **evidence["artifact_sha256"],
            "instrument_evidence.json": hashlib.sha256(evidence_raw).hexdigest(),
        }
        manifest = {
            "artifacts": manifest_artifacts,
            "schema_version": "joulewise.instrument_validation_manifest.v1",
            "validation_id": attempt_id,
        }
        (custody / "manifest.json").write_text(
            json.dumps(manifest, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        return custody

    def _historical_fixture(self):
        checkout = self.root / "checkout"
        specifications = (
            ("20260101T000001-aaaaaaaa", "1", "valid"),
            ("20260101T000002-bbbbbbbb", "2", "systematic-invalid"),
            ("20260101T000003-cccccccc", "3", "ordinary-invalid"),
        )
        custodies = [
            self._historical_custody(
                checkout, "runs_fixture", attempt_id, token
            )
            for attempt_id, token, disposition in specifications
        ]
        members = []
        for custody, (attempt_id, token, disposition) in zip(
            custodies, specifications
        ):
            del token
            hashes = artifact_hashes(custody)
            self.assertEqual(set(hashes), set(GOVERNED_ARTIFACTS))
            members.append(
                {
                    "attempt_id": attempt_id,
                    "content_id": content_id_from_artifact_hashes(hashes),
                    "artifact_sha256": hashes,
                    "disposition": disposition,
                }
            )
        table = {
            "schema_version": HISTORICAL_IMPORT_TABLE_SCHEMA,
            "ledger_schema": LEDGER_SCHEMA,
            "identity_epoch": dict(self.epoch),
            "members": members,
        }
        return checkout, checkout / "runs_fixture", custodies, table

    def _historical_import_args(self, table: dict, custodies: list[Path]) -> dict:
        table_raw = (json.dumps(table, indent=2, sort_keys=True) + "\n").encode()
        manifest = {
            "schema_version": HISTORICAL_IMPORT_CUSTODY_MANIFEST_SCHEMA,
            "ledger_schema": LEDGER_SCHEMA,
            "members": {
                member["content_id"]: str(custody.resolve())
                for member, custody in zip(table["members"], custodies)
            },
        }
        manifest_raw = custody_manifest_bytes(manifest)
        return {
            "disposition_table_raw": table_raw,
            "expected_disposition_table_sha256": hashlib.sha256(
                table_raw
            ).hexdigest(),
            "custody_manifest_raw": manifest_raw,
            "expected_custody_manifest_sha256": hashlib.sha256(

exec
/bin/zsh -lc "sed -n '190,245p' tests/test_calibration_ledger.py" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
        )

    def _snapshot(self, *, verify_custody: bool = True):
        return load_calibration_ledger_snapshot(
            self.ledger,
            self.pin,
            baseline_sequence=0,
            baseline_digest=GENESIS_DIGEST,
            require_committed_pin=False,
            verify_custody=verify_custody,
        )

    def _historical_custody(
        self,
        checkout: Path,
        run_name: str,
        attempt_id: str,
        token: str,
    ) -> Path:
        custody = checkout / run_name / "instrument_validation" / attempt_id
        (custody / "raw").mkdir(parents=True)
        payloads = {
            "raw/powermetrics.plist": f"raw-{token}\n".encode(),
            "events.jsonl": (
                json.dumps({"event_type": "capture", "token": token}) + "\n"
            ).encode(),
            "power_trace.csv": f"timestamp_s,gpu_w\n1,{token}\n".encode(),
        }
        for relative, raw in payloads.items():
            (custody / relative).write_bytes(raw)
        bound = f"0.0{int(token) + 1}"
        evidence = {
            "artifact_sha256": {
                name: hashlib.sha256(raw).hexdigest()
                for name, raw in payloads.items()
            },
            "b_fiducial_s": float(bound),
            "bindings": dict(self.t1),
            "capture_wall_time_s": 1000.0 + int(token),
            # Deliberately non-authoritative and contrary to some ruled rows.
            "status": "valid" if int(token) % 2 else "invalid",
            "validation_id": attempt_id,
        }
        evidence_raw = (
            json.dumps(evidence, indent=2, sort_keys=True) + "\n"
        ).encode()
        (custody / "instrument_evidence.json").write_bytes(evidence_raw)
        manifest_artifacts = {
            **evidence["artifact_sha256"],
            "instrument_evidence.json": hashlib.sha256(evidence_raw).hexdigest(),
        }
        manifest = {
            "artifacts": manifest_artifacts,
            "schema_version": "joulewise.instrument_validation_manifest.v1",
            "validation_id": attempt_id,
        }

exec
/bin/zsh -lc "git show impl/d117-u1-ledger-session:joulewise/calibration_bracketing.py | sed -n '735,930p'; git show impl/d117-u1-ledger-session:tests/test_calibration_bracketing.py | sed -n '1900,2010p'; rg -n \"instrument_binding_evidence.v1|binding_evidence\" tests | head -n 80" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
        and binding_evidence.get("binding_vector_sha256")
        == hashlib.sha256(canonical).hexdigest()
        and isinstance(binary, Mapping)
        and binary.get("sha256") == bindings.get("powermetrics_sha256")
        and isinstance(binary.get("path"), str)
        and bool(binary.get("path"))
        and isinstance(power_policy, Mapping)
        and power_policy.get("id") == bindings.get("power_policy")
    )


def load_calibration_candidate(
    directory: Path, *, runs_root: Path
) -> CalibrationCandidate | None:
    """Authenticate one standalone validation directory from primary bytes."""

    root = Path(runs_root).resolve()
    try:
        directory = Path(directory).resolve(strict=True)
        relative = directory.relative_to(root).as_posix()
        manifest_raw = (directory / "manifest.json").read_bytes()
        manifest = json.loads(manifest_raw)
    except (OSError, ValueError, UnicodeDecodeError, json.JSONDecodeError):
        return None
    artifacts = manifest.get("artifacts") if isinstance(manifest, Mapping) else None
    if (
        not relative
        or not isinstance(artifacts, Mapping)
        or manifest.get("schema_version")
        != "joulewise.instrument_validation_manifest.v1"
    ):
        return None
    members: dict[str, bytes] = {}
    for name, expected in artifacts.items():
        if not isinstance(name, str) or Path(name).is_absolute() or ".." in Path(name).parts:
            return None
        try:
            member = (directory / name).resolve(strict=True)
            member.relative_to(directory)
            raw = member.read_bytes()
        except (OSError, ValueError):
            return None
        if not _valid_sha256(expected) or hashlib.sha256(raw).hexdigest() != expected:
            return None
        members[name] = raw
    try:
        evidence_raw = members["instrument_evidence.json"]
        events_raw = members["events.jsonl"]
        powermetrics_raw = members["raw/powermetrics.plist"]
        evidence = json.loads(evidence_raw)
    except (KeyError, UnicodeDecodeError, json.JSONDecodeError):
        return None
    if not isinstance(evidence, Mapping):
        return None
    protocol_id = evidence.get("protocol_id")
    bindings = evidence.get("bindings")
    capture = evidence.get(CAPTURE_TIME_FIELD)
    if (
        protocol_id not in {PROTOCOL_V2_ID, PROTOCOL_ID}
        or evidence.get("schema_version") != "joulewise.instrument_evidence.v1"
        or manifest.get("protocol_id") != protocol_id
        or manifest.get("pulse_count") != protocol_pulse_count(str(protocol_id))
        or not isinstance(bindings, Mapping)
        or any(bindings.get(field) in (None, "") for field in V2_BINDING_FIELDS)
        or not _binding_evidence_authentic(evidence, bindings)
        or bindings.get("pulse_protocol_id") != protocol_id
        or bindings.get("protocol_sha256") != protocol_sha256(str(protocol_id))
        or evidence.get("pulse_count") != protocol_pulse_count(str(protocol_id))
        or evidence.get("anchor_method_version")
        != "powermetrics_native_second_censored_intersection_v1"
        or evidence.get("residual_region_method") != RESIDUAL_REGION_METHOD
        or not isinstance(
            evidence.get("residual_region_coverage_assumption"), str
        )
        or not evidence.get("residual_region_coverage_assumption")
        or evidence.get("residual_region_coverage_resolution_s")
        != REGION_COVERAGE_RESOLUTION_S
        or evidence.get("max_age_s") != MAX_AGE_S
        or isinstance(capture, bool)
        or not isinstance(capture, int | float)
        or not math.isfinite(float(capture))
        or float(capture) < 0.0
    ):
        return None
    artifact_hashes = evidence.get("artifact_sha256")
    if (
        not isinstance(artifact_hashes, Mapping)
        or artifact_hashes.get("events.jsonl")
        != hashlib.sha256(events_raw).hexdigest()
        or artifact_hashes.get("raw/powermetrics.plist")
        != hashlib.sha256(powermetrics_raw).hexdigest()
    ):
        return None
    try:
        authenticated_capture = capture_wall_time_from_events(events_raw)
        effective_bound = verify_stored_evidence_physics(
            evidence, powermetrics_raw, events_raw
        )
    except (KeyError, TypeError, ValueError):
        return None
    if abs(float(capture) - authenticated_capture) > 1.0:
        return None
    try:
        decimal_evidence = json.loads(
            evidence_raw,
            parse_float=str,
            parse_int=str,
        )
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None
    stored_lexeme = (
        decimal_evidence.get("b_fiducial_s")
        if isinstance(decimal_evidence, Mapping)
        else None
    )
    stored_decimal = _decimal(stored_lexeme)
    if (
        stored_decimal is not None
        and float(stored_decimal) == float(effective_bound)
    ):
        effective_bound_lexeme = stored_lexeme
    else:
        # A physical re-fit can widen beyond the stored scalar. Its returned
        # representation becomes the re-derivation source lexeme; no later
        # acceptance comparison converts that value through binary64 again.
        effective_bound_lexeme = str(float(effective_bound))
    return CalibrationCandidate(
        relative_path=relative,
        manifest_sha256=hashlib.sha256(manifest_raw).hexdigest(),
        evidence_sha256=hashlib.sha256(evidence_raw).hexdigest(),
        protocol_id=str(protocol_id),
        capture_wall_time_s=float(capture),
        b_fiducial_s=effective_bound_lexeme,
        bindings=dict(bindings),
    )


def _candidate_from_observation(
    observation: LedgerObservation,
) -> CalibrationCandidate | None:
    """Authenticate one valid ledger observation from its custody locator."""

    if observation.disposition != "valid" or observation.content_id is None:
        return None
    custody = Path(observation.custody_locator)
    candidate = load_calibration_candidate(
        custody,
        runs_root=custody.parent.parent,
    )
    if candidate is None:
        return None
    bound = _candidate_decimal(candidate)
    receipt_bound = _decimal(observation.exact_bound_lexeme_s)
    try:
        receipt_capture = float(observation.capture_wall_time_s)
    except (TypeError, ValueError):
        return None
    if (
        candidate.manifest_sha256
        != observation.artifact_sha256.get("manifest.json")
        or candidate.evidence_sha256
        != observation.artifact_sha256.get("instrument_evidence.json")
        or content_id_from_artifact_hashes(observation.artifact_sha256)
        != observation.content_id
        or bound is None
        or receipt_bound is None
        or bound != receipt_bound
        or candidate.capture_wall_time_s != receipt_capture
        or any(
            candidate.bindings.get(field) != observation.t1_bindings.get(field)
            for field in V2_BINDING_FIELDS
        )
        or any(
            candidate.bindings.get(field) != observation.identity_epoch.get(field)
            for field in ACCEPTANCE_IDENTITY_FIELDS
        )
    ):
        return None
    return replace(
        candidate,
        relative_path=observation.custody_locator,
        attempt_id=observation.attempt_id,
        content_id=observation.content_id,
        ledger_receipt_digest=observation.receipt_digest,
        bracket_session_id=observation.bracket_session_id,
        bracket_slot=observation.bracket_slot,
        bracket_window_id=observation.bracket_window_id,
        bracket_plan_id=observation.bracket_plan_id,
        bracket_plan_sha256=observation.bracket_plan_sha256,
        bracket_evidence_root_id=observation.bracket_evidence_root_id,
        bracket_runs_root=observation.bracket_runs_root,
    )


def discover_calibration_candidates(
    ledger_snapshot: CalibrationLedgerSnapshot,
                    "powermetrics_native_second_censored_intersection_v1"
                ),
                "pulse_protocol_id": PROTOCOL_ID,
                "protocol_sha256": PROTOCOL_V3_SHA256,
                "estimator_revision": RESIDUAL_REGION_METHOD,
            }
        )
        canonical = json.dumps(
            bindings,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        ).encode("utf-8")
        events = b'{"timestamp_s":99.0}\n'
        raw = b"authenticated-by-patched-physics"
        evidence = {
            "schema_version": "joulewise.instrument_evidence.v1",
            "protocol_id": PROTOCOL_ID,
            "pulse_count": PULSE_COUNT,
            "anchor_method_version": bindings["anchor_method_version"],
            "residual_region_method": RESIDUAL_REGION_METHOD,
            "residual_region_coverage_assumption": "complete accepted region",
            "residual_region_coverage_resolution_s": (
                REGION_COVERAGE_RESOLUTION_S
            ),
            "capture_wall_time_s": 99.0,
            "b_fiducial_s": 0.02,
            "max_age_s": MAX_AGE_S,
            "bindings": bindings,
            "binding_evidence": {
                "schema_version": "joulewise.instrument_binding_evidence.v1",
                "binding_vector_sha256": hashlib.sha256(canonical).hexdigest(),
                "powermetrics_binary": {
                    "path": "/usr/bin/powermetrics",
                    "sha256": bindings["powermetrics_sha256"],
                },
                "power_policy": {"id": bindings["power_policy"]},
            },
            "artifact_sha256": {
                "events.jsonl": hashlib.sha256(events).hexdigest(),
                "raw/powermetrics.plist": hashlib.sha256(raw).hexdigest(),
            },
        }
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            directory = root / "instrument_validation" / "candidate"
            (directory / "raw").mkdir(parents=True)
            (directory / "events.jsonl").write_bytes(events)
            (directory / "raw/powermetrics.plist").write_bytes(raw)

            def write_evidence_and_manifest() -> None:
                evidence_raw = json.dumps(evidence, sort_keys=True).encode()
                (directory / "instrument_evidence.json").write_bytes(evidence_raw)
                artifacts = {
                    "events.jsonl": hashlib.sha256(events).hexdigest(),
                    "raw/powermetrics.plist": hashlib.sha256(raw).hexdigest(),
                    "instrument_evidence.json": hashlib.sha256(
                        evidence_raw
                    ).hexdigest(),
                }
                (directory / "manifest.json").write_text(
                    json.dumps(
                        {
                            "schema_version": (
                                "joulewise.instrument_validation_manifest.v1"
                            ),
                            "protocol_id": PROTOCOL_ID,
                            "pulse_count": PULSE_COUNT,
                            "artifacts": artifacts,
                        }
                    )
                )

            write_evidence_and_manifest()
            with patch(
                "joulewise.calibration_bracketing.verify_stored_evidence_physics",
                return_value=0.02,
            ):
                candidate = load_calibration_candidate(
                    directory, runs_root=root
                )
                self.assertIsNotNone(candidate)
                self.assertEqual(candidate.b_fiducial_s, "0.02")
                evidence["bindings"]["hardware_model"] = "tampered-model"
                write_evidence_and_manifest()
                self.assertIsNone(
                    load_calibration_candidate(directory, runs_root=root)
                )


if __name__ == "__main__":
    unittest.main()
tests/test_calibration_bracketing.py:1567:            "binding_evidence": {
tests/test_calibration_bracketing.py:1568:                "schema_version": "joulewise.instrument_binding_evidence.v1",
tests/test_p2038_production_path.py:177:    evidence["binding_evidence"] = {
tests/test_p2038_production_path.py:178:        "schema_version": "joulewise.instrument_binding_evidence.v1",
tests/test_reduce.py:2800:        evidence["binding_evidence"] = {
tests/test_reduce.py:2801:            "schema_version": "joulewise.instrument_binding_evidence.v1",
tests/test_reduce.py:2823:        evidence["binding_evidence"]["binding_vector_sha256"] = hashlib.sha256(
tests/test_reduce.py:3276:        evidence["binding_evidence"]["binding_vector_sha256"] = hashlib.sha256(
tests/test_reduce.py:3650:        evidence["binding_evidence"] = {
tests/test_reduce.py:3651:            "schema_version": "joulewise.instrument_binding_evidence.v1",

exec
/bin/zsh -lc "git show impl/d117-u1-ledger-session:joulewise/calibration_bracketing.py | sed -n '960,1225p'" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
        if candidate is None:
            return ()
        candidates.append(candidate)
    return tuple(candidates)


def _prior_set_matches_import_cutoff_prefix(
    artifact: Mapping[str, Any],
    ledger_snapshot: CalibrationLedgerSnapshot,
) -> bool:
    """Bind issuance prior-set data to the import-marked cutoff prefix."""

    cutoff = artifact["ledger_cutoff"]
    prefix = tuple(
        observation
        for observation in ledger_snapshot.observations
        if observation.sequence <= cutoff["sequence"]
    )
    # The checked-in schema fixture predates issuance and deliberately has a
    # genesis cutoff. Production issuance, or any fixture containing imported
    # prefix rows, must satisfy the exact marker-bound comparison below.
    if not prefix and artifact.get("artifact_role") == "schema_fixture_unissued":
        return True
    if any(not observation.is_historical_import for observation in prefix):
        return False
    catalog = artifact["prior_observation_set"]["epoch_catalog"]
    expected = {
        (
            row["attempt_id"],
            row["content_id"],
            row["disposition"],
            row["epoch_id"],
        )
        for row in artifact["prior_observation_set"]["observations"]
    }
    observed: set[tuple[str, str, str, str]] = set()
    for observation in prefix:
        epoch_ids = [
            epoch_id
            for epoch_id, epoch in catalog.items()
            if dict(epoch) == dict(observation.identity_epoch)
        ]
        if observation.content_id is None or len(epoch_ids) != 1:
            return False
        observed.add(
            (
                observation.attempt_id,
                observation.content_id,
                observation.classification_disposition,
                epoch_ids[0],
            )
        )
    return observed == expected and len(observed) == len(prefix)


def evaluate_calibration_bracket(
    candidates: Sequence[CalibrationCandidate],
    *,
    window_start_s: float,
    window_end_s: float,
    bindings: Mapping[str, Any],
    policy: CalibrationBracketingPolicy,
    acceptance_bound: Mapping[str, Any] | None = None,
    ledger_snapshot: CalibrationLedgerSnapshot | None = None,
    bracket_binding: Mapping[str, Any] | None = None,
    bracket_window_id: str | None = None,
    bracket_plan_id: str | None = None,
    bracket_plan_sha256: str | None = None,
    bracket_evidence_root_id: str | None = None,
    bracket_runs_root: Path | str | None = None,
    _allow_unissued_fixture: bool = False,
) -> tuple[dict[str, Any], tuple[str, ...]]:
    """Select a causal bracket and apply the provenance-bound D-079 budget."""

    result: dict[str, Any] = {
        "schema_version": BRACKET_SCHEMA,
        "policy": {
            "require_bracket": policy.require_bracket,
            "calibration_bracket_max_drift_s": (
                policy.calibration_bracket_max_drift_s
            ),
        },
        "window_start_s": window_start_s,
        "window_end_s": window_end_s,
        "pre": None,
        "post": None,
        "endpoint_max_b_fiducial_s": None,
        "calibration_drift_allowance_s": None,
        "b_fiducial_s": None,
        "drift_s": None,
        "acceptance": None,
        "bracket_binding": None,
        "status": "not_required" if not policy.require_bracket else "failed",
    }
    if not policy.require_bracket:
        return result, ()
    if (
        not math.isfinite(window_start_s)
        or not math.isfinite(window_end_s)
        or window_start_s >= window_end_s
    ):
        return result, ("instrument_calibration_bracket_missing",)

    using_default_bound = acceptance_bound is None
    artifact = (
        load_calibration_acceptance_bound()
        if using_default_bound
        else _authenticated_explicit_acceptance_bound(acceptance_bound)
    )
    if artifact is None:
        result["acceptance"] = {
            "schema_version": ACCEPTANCE_EVALUATION_SCHEMA,
            "artifact": None,
            "freshness": {
                "status": "stale",
                "reason": "acceptance_artifact_missing_or_invalid",
            },
        }
        return result, ("calibration_acceptance_bound_stale",)
    artifact_role = artifact["artifact_role"]
    artifact_sha256 = _acceptance_artifact_sha256(artifact)
    if artifact_role == "schema_fixture_unissued" and not _allow_unissued_fixture:
        result["acceptance"] = {
            "schema_version": ACCEPTANCE_EVALUATION_SCHEMA,
            "artifact": {
                "acceptance_id": artifact["acceptance_id"],
                "artifact_sha256": artifact_sha256,
                "authentication": "checked_in_genesis_fixture_byte_sha256_pin",
                "artifact_role": artifact_role,
                "claim_eligible": False,
            },
            "freshness": {
                "status": "stale",
                "reason": "acceptance_artifact_unissued_fixture",
            },
        }
        return result, ("calibration_acceptance_bound_stale",)
    cutoff = artifact["ledger_cutoff"]
    result["acceptance"] = {
        "schema_version": ACCEPTANCE_EVALUATION_SCHEMA,
        "artifact": {
            "acceptance_id": artifact["acceptance_id"],
            "artifact_sha256": artifact_sha256,
            "authentication": (
                "checked_in_issued_artifact_byte_sha256_pin"
                if artifact_role == "issued"
                else "checked_in_genesis_fixture_byte_sha256_pin"
            ),
            "artifact_role": artifact_role,
            "claim_eligible": False,
        },
        "freshness": {
            "status": "stale",
            "reason": "acceptance_artifact_ledger_authentication_pending",
        },
    }
    if ledger_snapshot is None:
        return result, ("calibration_ledger_snapshot_required",)
    if ledger_snapshot.refusal_reasons:
        return result, tuple(ledger_snapshot.refusal_reasons)
    if (
        ledger_snapshot.baseline_sequence != cutoff["sequence"]
        or ledger_snapshot.baseline_digest != cutoff["head_digest"]
        or ledger_snapshot.ledger_schema != cutoff["ledger_schema"]
        or artifact_role == "issued"
        and (
            ledger_snapshot.head_sequence <= 0
            or ledger_snapshot.head_digest == "0" * 64
        )
    ):
        return result, ("calibration_ledger_baseline_missing",)
    if not _prior_set_matches_import_cutoff_prefix(artifact, ledger_snapshot):
        return result, ("calibration_ledger_baseline_missing",)
    identity_epoch = artifact["identity_epoch"]
    prospective = artifact["prospective_rederivation"]
    result["policy"].update(
        {
            "calibration_bracket_max_drift_s_role": (
                "legacy_obsolete_not_an_acceptance_comparator"
            ),
            "acceptance_bound_id": artifact["acceptance_id"],
            "operative_bracket_screen_decimal_s": (
                artifact["decimal_derivation"]["ratified_operatives"][
                    "bracket_screen_s"
                ]
            ),
        }
    )
    observed_identity = {
        field: bindings.get(field) for field in ACCEPTANCE_IDENTITY_FIELDS
    }
    stale_fields = [
        field
        for field in ACCEPTANCE_IDENTITY_FIELDS
        if observed_identity.get(field) != identity_epoch.get(field)
    ]
    freshness_status = "stale" if stale_fields else "fresh"
    result["acceptance"] = {
        "schema_version": ACCEPTANCE_EVALUATION_SCHEMA,
        "artifact": {
            "acceptance_id": artifact["acceptance_id"],
            "artifact_sha256": artifact_sha256,
            "authentication": (
                "checked_in_issued_artifact_byte_sha256_pin"
                if artifact_role == "issued"
                else "checked_in_genesis_fixture_byte_sha256_pin"
            ),
            "artifact_role": artifact_role,
            "claim_eligible": artifact_role == "issued",
            "derivation_sha256": artifact["derivation_sha256"],
        },
        "freshness": {
            "status": freshness_status,
            "basis": "exact_identity_epoch",
            "expected_identity_epoch": dict(identity_epoch),
            "observed_identity_epoch": observed_identity,
            "trigger_guard_protocol_sha256": prospective["protocol_sha256"],
            "trigger_guard_estimator_code_sha256": dict(
                prospective["estimator_code_sha256"]
            ),
            "stale_fields": stale_fields,
            "calendar_expiry": None,
        },
        "prospective_rederivation": {
            "observation_rule": prospective["trigger_observation_rule"],
            "candidate_set_boundary": (
                "authenticated_calibration_ledger_snapshot_only"
            ),
            "global_runs_root_scan": False,
            "mandatory_triggers": list(prospective["triggers"]),
            "observed_triggers": [],
        },
        "numeric_semantics": {
            "comparisons": "decimal",
            "reducer_boundary": "binary64_recorded_below",
        },
        "ledger_snapshot": {
            "ledger_schema": ledger_snapshot.ledger_schema,
            "sequence": ledger_snapshot.head_sequence,
            "head_digest": ledger_snapshot.head_digest,
            "baseline_sequence": ledger_snapshot.baseline_sequence,
            "baseline_digest": ledger_snapshot.baseline_digest,
            "load_count": 1,
        },
        "preflight": None,
        "drift": None,
    }
    if stale_fields:
        return result, ("calibration_acceptance_bound_stale",)
    observations_by_attempt = ledger_snapshot.observation_by_attempt
    finalized_session_ids = {
        session.session_id
        for session in ledger_snapshot.bracket_sessions
        if session.state == "finalized"
    }
    registered_valid = {
        (
            observation.attempt_id,
            observation.content_id,
            observation.receipt_digest,
        )
        for observation in ledger_snapshot.observations
        if observation.disposition == "valid"
        and not observation.is_historical_import
        and (
            observation.bracket_session_id is None

exec
/bin/zsh -lc "git show impl/d117-u1-ledger-session:joulewise/calibration_bracketing.py | sed -n '150,530p' | rg -n \"ISSUED|authenticated|sha256|artifact_role|return\" -C 3; git show impl/d117-u1-ledger-session:joulewise/calibration_bracketing.py | sed -n '430,530p'" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
1-        result = _decimal(value)
2-        if result is None:
3:            return None
4-    elif (
5-        isinstance(value, int | float)
6-        and not isinstance(value, bool)
7-        and math.isfinite(float(value))
8-    ):
9-        # Compatibility for synthetic callers that predate D-102. Production
10:        # candidates carry strings from authenticated evidence bytes instead.
11-        result = Decimal(str(value))
12-    else:
13:        return None
14:    return result if result.is_finite() else None
15-
16-
17:def _current_estimator_code_sha256() -> dict[str, str] | None:
18-    try:
19:        return {
20:            relative: hashlib.sha256((_REPO_ROOT / relative).read_bytes()).hexdigest()
21-            for relative in ESTIMATOR_CODE_PATHS
22-        }
23-    except OSError:
24:        return None
25-
26-
27-def _valid_acceptance_bound(value: Any) -> bool:
28-    """Validate the D-102 artifact from its decimal-source member table."""
29-
30-    if not isinstance(value, Mapping):
31:        return False
32:    core = {key: item for key, item in value.items() if key != "derivation_sha256"}
33-    identity = value.get("identity_epoch")
34-    prospective = value.get("prospective_rederivation")
35-    corpus = value.get("derivation_corpus")
--
38-    issuance = value.get("issuance")
39-    backfill = value.get("backfill_candidate")
40-    derivation = value.get("decimal_derivation")
41:    role = value.get("artifact_role")
42-    if role == "schema_fixture_unissued":
43-        role_valid = (
44-            value.get("schema_version") == ACCEPTANCE_FIXTURE_SCHEMA
--
71-            and isinstance(cutoff.get("sequence"), int)
72-            and not isinstance(cutoff.get("sequence"), bool)
73-            and cutoff.get("sequence") > 0
74:            and _valid_sha256(cutoff.get("head_digest"))
75-            and cutoff.get("head_digest") != "0" * 64
76-            and cutoff.get("role") == "issued_acceptance_baseline"
77-            and isinstance(backfill, Mapping)
--
84-            "ordinary-invalid",
85-        }
86-    else:
87:        return False
88-    if (
89-        not role_valid
90-        or value.get("acceptance_id") != "d079_calibration_acceptance_v2_n19"
91-        or value.get("decision_ids") != ["D-102", "D-109"]
92:        or value.get("derivation_sha256") != _canonical_sha256(core)
93-        or not isinstance(identity, Mapping)
94-        or set(identity) != set(ACCEPTANCE_IDENTITY_FIELDS)
95-        or any(identity.get(field) in (None, "") for field in ACCEPTANCE_IDENTITY_FIELDS)
--
97-        or prospective.get("calendar_expiry") is not None
98-        or prospective.get("trigger_observation_rule")
99-        != "judge_under_prior_artifact_never_self_fit"
100:        or prospective.get("protocol_sha256") != protocol_sha256(PROTOCOL_ID)
101:        or not isinstance(prospective.get("estimator_code_sha256"), Mapping)
102:        or set(prospective["estimator_code_sha256"]) != set(ESTIMATOR_CODE_PATHS)
103-        or any(
104:            not _valid_sha256(item)
105:            for item in prospective["estimator_code_sha256"].values()
106-        )
107-        or not isinstance(prospective.get("triggers"), list)
108-        or set(prospective["triggers"])
--
133-        or not isinstance(derivation, Mapping)
134-        or derivation.get("numeric_semantics") != "decimal_source_lexemes"
135-    ):
136:        return False
137-    member_ids: list[str] = []
138-    values: list[Decimal] = []
139-    for member in corpus["members"]:
--
144-                "member_id",
145-                "source_directory",
146-                "b_fiducial_s",
147:                "manifest_sha256",
148:                "instrument_evidence_sha256",
149-            }
150-            or not isinstance(member.get("member_id"), str)
151-            or not isinstance(member.get("source_directory"), str)
152:            or not _valid_sha256(member.get("manifest_sha256"))
153:            or not _valid_sha256(member.get("instrument_evidence_sha256"))
154-        ):
155:            return False
156-        bound = _decimal(member.get("b_fiducial_s"))
157-        if bound is None or bound < 0:
158:            return False
159-        member_ids.append(member["member_id"])
160-        values.append(bound)
161-    if len(set(member_ids)) != 19 or member_ids != sorted(member_ids):
162:        return False
163-
164-    prior_ids: list[str] = []
165-    prior_attempt_ids: list[str] = []
--
169-            not isinstance(observation, Mapping)
170-            or set(observation)
171-            != {"content_id", "epoch_id", "disposition", "attempt_id"}
172:            or not _valid_sha256(observation.get("content_id"))
173-            or observation.get("epoch_id") != "d079_epoch"
174-            or observation.get("disposition") not in allowed_prior_dispositions
175-            or not isinstance(observation.get("attempt_id"), str)
176-            or not observation.get("attempt_id")
177-        ):
178:            return False
179-        prior_ids.append(observation["content_id"])
180-        prior_attempt_ids.append(observation["attempt_id"])
181-        if observation["attempt_id"] in member_ids:
--
185-        or len(prior_attempt_ids) != len(set(prior_attempt_ids))
186-        or prior_member_ids != set(member_ids)
187-    ):
188:        return False
189-    if role == "issued":
190-        disposition_counts = {
191-            disposition: sum(
--
199-            or cutoff["sequence"] != 2 * len(prior["observations"])
200-            or backfill.get("candidate_inventory") != disposition_counts
201-        ):
202:            return False
203-    member_content_ids = {
204-        content_id_from_artifact_hashes(
205-            {
206:                "manifest.json": member["manifest_sha256"],
207-                "instrument_evidence.json": member[
208:                    "instrument_evidence_sha256"
209-                ],
210-            }
211-        )
212-        for member in corpus["members"]
213-    }
214-    if None in member_content_ids or not member_content_ids.issubset(set(prior_ids)):
215:        return False
216-
217-    statistics = derivation.get("source_statistics")
218-    rounding = derivation.get("rounding")
219-    operatives = derivation.get("ratified_operatives")
220-    if not all(isinstance(item, Mapping) for item in (statistics, rounding, operatives)):
221:        return False
222-    with localcontext() as context:
223-        context.prec = 80
224-        count = Decimal(len(values))
--
277-        != "max(pre_b_fiducial_s,post_b_fiducial_s)+calibration_drift_allowance_s"
278-        or operatives.get("embedding_count") != 1
279-    ):
280:        return False
281-    screen = Decimal(_D102_OPERATIVE_VALUES["bracket_screen_s"])
282-    maximum = Decimal(_D102_OPERATIVE_VALUES["maximum_budgetable_drift_s"])
283-    excess = Decimal(_D102_OPERATIVE_VALUES["max_budgetable_excess_s"])
284:    return (
285-        (max(values) - min(values)).quantize(
286-            Decimal("0.000001"), rounding=ROUND_HALF_EVEN
287-        )
--
302-    try:
303-        raw = Path(path).read_bytes()
304-    except OSError:
305:        return None
306:    return _acceptance_bound_from_authenticated_bytes(raw)
307-
308-
309:def _acceptance_bound_from_authenticated_bytes(
310-    raw: bytes,
311-) -> dict[str, Any] | None:
312-    """Parse acceptance bytes only when their role-indexed pin authenticates."""
--
314-    try:
315-        value = json.loads(raw)
316-    except (UnicodeDecodeError, json.JSONDecodeError):
317:        return None
318:    # Any file route is authenticated by one of the two reviewed exact-byte
319-    # states: the genesis fixture retained for pre-issuance tests, or the
320-    # deterministically emitted issued artifact. A caller cannot turn an
321-    # alternate self-consistent document into authority by choosing a path.
322:    expected_sha256 = {
323-        "schema_fixture_unissued": DEFAULT_ACCEPTANCE_BOUND_SHA256,
324:        "issued": ISSUED_ACCEPTANCE_BOUND_SHA256,
325:    }.get(value.get("artifact_role") if isinstance(value, Mapping) else None)
326:    if hashlib.sha256(raw).hexdigest() != expected_sha256:
327:        return None
328-    if not _valid_acceptance_bound(value):
329:        return None
330:    return dict(value)
331-
332-
333:def _authenticated_explicit_acceptance_bound(
334-    value: Mapping[str, Any],
335-) -> dict[str, Any] | None:
336-    """Authenticate an in-memory artifact against the checked-in byte pin."""
337-
338-    pinned = load_calibration_acceptance_bound()
339-    if pinned is None or dict(value) != pinned:
340:        return None
341:    return pinned
342-
343-
344:def _acceptance_artifact_sha256(artifact: Mapping[str, Any]) -> str:
345-    """Return the reviewed exact-byte pin for a validated artifact role."""
346-
347:    return (
348:        ISSUED_ACCEPTANCE_BOUND_SHA256
349:        if artifact.get("artifact_role") == "issued"
350-        else DEFAULT_ACCEPTANCE_BOUND_SHA256
351-    )
352-
353-
354:def _valid_sha256(value: Any) -> bool:
355:    return (
356-        isinstance(value, str)
357-        and len(value) == 64
358-        and all(char in "0123456789abcdef" for char in value)
--
365-    "session_id",
366-    "window_id",
367-    "plan_id",
368:    "plan_sha256",
369-    "evidence_root_id",
370-    "runs_root",
371-    "capability_receipt_digest",
    screen = Decimal(_D102_OPERATIVE_VALUES["bracket_screen_s"])
    maximum = Decimal(_D102_OPERATIVE_VALUES["maximum_budgetable_drift_s"])
    excess = Decimal(_D102_OPERATIVE_VALUES["max_budgetable_excess_s"])
    return (
        (max(values) - min(values)).quantize(
            Decimal("0.000001"), rounding=ROUND_HALF_EVEN
        )
        == screen
        and max(values).quantize(
            Decimal("0.000000000000001"), rounding=ROUND_HALF_EVEN
        )
        == Decimal(_D102_OPERATIVE_VALUES["preflight_level_screen_s"])
        and screen + excess == maximum
    )


def load_calibration_acceptance_bound(
    path: Path = DEFAULT_ACCEPTANCE_BOUND_PATH,
) -> dict[str, Any] | None:
    """Load the file-pinned D-102 acceptance artifact fail-closed."""

    try:
        raw = Path(path).read_bytes()
    except OSError:
        return None
    return _acceptance_bound_from_authenticated_bytes(raw)


def _acceptance_bound_from_authenticated_bytes(
    raw: bytes,
) -> dict[str, Any] | None:
    """Parse acceptance bytes only when their role-indexed pin authenticates."""

    try:
        value = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None
    # Any file route is authenticated by one of the two reviewed exact-byte
    # states: the genesis fixture retained for pre-issuance tests, or the
    # deterministically emitted issued artifact. A caller cannot turn an
    # alternate self-consistent document into authority by choosing a path.
    expected_sha256 = {
        "schema_fixture_unissued": DEFAULT_ACCEPTANCE_BOUND_SHA256,
        "issued": ISSUED_ACCEPTANCE_BOUND_SHA256,
    }.get(value.get("artifact_role") if isinstance(value, Mapping) else None)
    if hashlib.sha256(raw).hexdigest() != expected_sha256:
        return None
    if not _valid_acceptance_bound(value):
        return None
    return dict(value)


def _authenticated_explicit_acceptance_bound(
    value: Mapping[str, Any],
) -> dict[str, Any] | None:
    """Authenticate an in-memory artifact against the checked-in byte pin."""

    pinned = load_calibration_acceptance_bound()
    if pinned is None or dict(value) != pinned:
        return None
    return pinned


def _acceptance_artifact_sha256(artifact: Mapping[str, Any]) -> str:
    """Return the reviewed exact-byte pin for a validated artifact role."""

    return (
        ISSUED_ACCEPTANCE_BOUND_SHA256
        if artifact.get("artifact_role") == "issued"
        else DEFAULT_ACCEPTANCE_BOUND_SHA256
    )


def _valid_sha256(value: Any) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(char in "0123456789abcdef" for char in value)
    )


_BRACKET_BINDING_KEYS = {
    "schema_version",
    "ledger_schema",
    "session_id",
    "window_id",
    "plan_id",
    "plan_sha256",
    "evidence_root_id",
    "runs_root",
    "capability_receipt_digest",
    "terminal_head",
    "endpoints",
    "binding_digest",
}
_BRACKET_ENDPOINT_KEYS = {
    "attempt_id",
    "receipt_digest",
    "content_digest",
}


exec
/bin/zsh -lc "python3 - <<'PY'
from joulewise.powermetrics_fiducial import V2_BINDING_FIELDS
print(V2_BINDING_FIELDS)
PY
git show impl/d117-u1-ledger-session:joulewise/calibration_ledger.py | sed -n '2970,3045p'; git show impl/d117-u1-ledger-session:joulewise/calibration_bracketing.py | sed -n '1,80p'" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
('hardware_model', 'os_build', 'powermetrics_sha256', 'sampling_interval_ms', 'anchor_method_version', 'mlx_version', 'pulse_protocol_id', 'power_policy', 'estimator_revision', 'protocol_sha256')
            "bracket session receipts require terminal_head_pin_for_session"
        )
    return _head_pin_for_valid_receipt(receipt)


__all__ = [
    "ALL_DISPOSITIONS",
    "BRACKET_SESSION_ABORT_EVENT",
    "BRACKET_SESSION_FINALIZATION_EVENT",
    "BRACKET_SESSION_OPEN_EVENT",
    "BRACKET_SESSION_SLOT_CLAIM_EVENT",
    "BRACKET_SESSION_SCHEMA",
    "BRACKET_SESSION_SLOTS",
    "CONTENT_ID_ARTIFACTS",
    "DEFAULT_HEAD_PIN_PATH",
    "DEFAULT_LEDGER_PATH",
    "FINAL_DISPOSITIONS",
    "GENESIS_DIGEST",
    "GOVERNED_ARTIFACTS",
    "HISTORICAL_IMPORT_EVENT_PREFIX",
    "HISTORICAL_IMPORT_CUSTODY_MANIFEST_SCHEMA",
    "HISTORICAL_IMPORT_FINALIZATION_EVENT",
    "HISTORICAL_IMPORT_RESERVATION_EVENT",
    "HISTORICAL_IMPORT_TABLE_SCHEMA",
    "IDENTITY_EPOCH_FIELDS",
    "LEDGER_SCHEMA",
    "RECEIPT_SCHEMA",
    "REFUSAL_TAXONOMY",
    "CalibrationLedgerError",
    "CalibrationBracketSession",
    "CalibrationLedgerSnapshot",
    "HistoricalImportDurabilityUncertain",
    "HistoricalImportPlan",
    "LedgerObservation",
    "append_pending_receipt",
    "append_bracket_session_receipt",
    "claim_bracket_session_slot",
    "abort_bracket_session",
    "artifact_hashes",
    "bootstrap_historical_import",
    "custody_manifest_bytes",
    "canonical_sha256",
    "content_id_from_artifact_hashes",
    "finalize_attempt_receipt",
    "finalize_bracket_session_slot",
    "generate_historical_custody_manifest",
    "head_pin_for_receipt",
    "load_calibration_ledger_snapshot",
    "prepare_historical_import",
    "terminal_head_pin_for_session",
    "validate_bracket_session_reservation_inputs",
]
"""Claim-time pre/post powermetrics fiducial calibration bracketing.

The bracket carries a nonparametric 95/95 calibration-distribution bound into
claims only under the registered T1-T3 transfer assumptions; it does not turn
either finite sample maximum into an unconditional instrument property.
"""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass, replace
from decimal import Decimal, InvalidOperation, ROUND_HALF_EVEN, localcontext
from pathlib import Path
from typing import Any, Mapping, Sequence

from joulewise.bundle_read import BundleReadError, BundleReader
from joulewise.calibration_ledger import (
    IDENTITY_EPOCH_FIELDS,
    LEDGER_SCHEMA,
    CalibrationLedgerSnapshot,
    LedgerObservation,
    content_id_from_artifact_hashes,
)
from joulewise.powermetrics_fiducial import (
    CAPTURE_TIME_FIELD,
    MAX_AGE_S,
    PROTOCOL_ID,
    PROTOCOL_V2_ID,
    REGION_COVERAGE_RESOLUTION_S,
    RESIDUAL_REGION_METHOD,
    V2_BINDING_FIELDS,
    capture_wall_time_from_events,
    protocol_pulse_count,
    protocol_sha256,
    verify_stored_evidence_physics,
)
from joulewise.schemas import CalibrationBracketingPolicy

BRACKET_SCHEMA = "joulewise.instrument_calibration_bracket.v1"
BRACKET_BINDING_SCHEMA = "joulewise.calibration_bracket_binding.v1"
ACCEPTANCE_BOUND_SCHEMA = "joulewise.calibration_acceptance_bound.v2"
ACCEPTANCE_FIXTURE_SCHEMA = (
    "joulewise.calibration_acceptance_bound.v2.fixture.v1"
)
ACCEPTANCE_EVALUATION_SCHEMA = "joulewise.calibration_acceptance_evaluation.v2"
DEFAULT_ACCEPTANCE_BOUND_PATH = (
    Path(__file__).resolve().parents[1]
    / "configs"
    / "calibration"
    / "calibration_acceptance_d079_v2.json"
)
DEFAULT_ACCEPTANCE_BOUND_SHA256 = (
    "9a264c57fdc007de473872870f19a5e1c9bd9b11256c25266b0e3e50ebba0ceb"
)
ISSUED_ACCEPTANCE_BOUND_SHA256 = (
    "316113960c596a6f927987dbdf8f2bca4b0cca9ee4a59a540bbd32bba9048985"
)
_REPO_ROOT = Path(__file__).resolve().parents[1]
ESTIMATOR_CODE_PATHS = (
    "joulewise/powermetrics_fiducial.py",
    "joulewise/uncertainty_evidence.py",
    "joulewise/adapters/powermetrics.py",
    "joulewise/reduce.py",
)
ACCEPTANCE_IDENTITY_FIELDS = IDENTITY_EPOCH_FIELDS
_D102_OPERATIVE_VALUES = {
    "bracket_screen_s": "0.010818",
    "preflight_level_screen_s": "0.033558756679900",
    "max_budgetable_excess_s": "0.001275166090593858",
    "maximum_budgetable_drift_s": "0.012093166090593858",
}


@dataclass(frozen=True)
class CalibrationCandidate:
    relative_path: str
    manifest_sha256: str
    evidence_sha256: str

exec
/bin/zsh -lc "git show impl/d117-u1-ledger-session:joulewise/calibration_bracketing.py | sed -n '1440,1605p'" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
        candidate for candidate in matching if candidate.capture_wall_time_s <= window_start_s
    ]
    causal_post = [
        candidate for candidate in matching if candidate.capture_wall_time_s >= window_end_s
    ]
    fresh_pre = [
        candidate
        for candidate in causal_pre
        if window_end_s <= candidate.capture_wall_time_s + MAX_AGE_S
    ]
    fresh_post = [
        candidate
        for candidate in causal_post
        if candidate.capture_wall_time_s - window_start_s <= MAX_AGE_S
    ]
    if not fresh_pre or not fresh_post:
        reason = (
            "instrument_calibration_stale"
            if (causal_pre and not fresh_pre) or (causal_post and not fresh_post)
            else "instrument_calibration_bracket_missing"
        )
        return result, (reason,)
    if bound_observations is None:
        pre = max(fresh_pre, key=lambda candidate: candidate.capture_wall_time_s)
        post = min(fresh_post, key=lambda candidate: candidate.capture_wall_time_s)
    else:
        candidate_by_receipt = {
            candidate.ledger_receipt_digest: candidate for candidate in matching
        }
        pre = candidate_by_receipt.get(bound_observations[0].receipt_digest)
        post = candidate_by_receipt.get(bound_observations[1].receipt_digest)
        if pre not in fresh_pre or post not in fresh_post:
            return result, ("calibration_bracket_binding_invalid",)
    pre_decimal = matching_decimals[id(pre)]
    post_decimal = matching_decimals[id(post)]
    if (
        not pre_decimal.is_finite()
        or not post_decimal.is_finite()
        or pre_decimal < 0
        or post_decimal < 0
    ):
        return result, ("instrument_calibration_invalid",)
    if isinstance(pre.b_fiducial_s, float) and isinstance(
        post.b_fiducial_s, float
    ):
        # Old synthetic probes supplied only binary64 endpoints. Preserve their
        # source arithmetic without applying Decimal after a second rounding;
        # authenticated production candidates always use the exact branch.
        drift_decimal = Decimal(
            str(abs(pre.b_fiducial_s - post.b_fiducial_s))
        )
    else:
        drift_decimal = abs(pre_decimal - post_decimal)
    endpoint_max_decimal = max(pre_decimal, post_decimal)
    operatives = artifact["decimal_derivation"]["ratified_operatives"]
    screen = Decimal(operatives["bracket_screen_s"])
    preflight_screen = Decimal(operatives["preflight_level_screen_s"])
    maximum_drift = Decimal(operatives["maximum_budgetable_drift_s"])
    maximum_excess = Decimal(operatives["max_budgetable_excess_s"])
    result.update(
        {
            "pre": pre.descriptor(),
            "post": post.descriptor(),
            "endpoint_max_b_fiducial_s": float(endpoint_max_decimal),
            "drift_s": float(drift_decimal),
        }
    )
    result["acceptance"]["numeric_semantics"].update(
        {
            "pre_b_fiducial_binary64_s": float(pre_decimal),
            "pre_b_fiducial_decimal_s": str(pre_decimal),
            "post_b_fiducial_binary64_s": float(post_decimal),
            "post_b_fiducial_decimal_s": str(post_decimal),
            "observed_drift_decimal_s": str(drift_decimal),
        }
    )
    preflight_status = "passed" if pre_decimal <= preflight_screen else "failed"
    result["acceptance"]["preflight"] = {
        "status": preflight_status,
        "observed_pre_b_fiducial_s": str(pre_decimal),
        "level_screen_s": str(preflight_screen),
        "failure_class": (
            None if preflight_status == "passed" else "systematic_not_budgetable"
        ),
    }
    if pre_decimal > preflight_screen:
        observed_triggers.append(
            "new_systematic_failure_challenges_preflight_screen"
        )
        result["acceptance"]["drift"] = {
            "status": "not_evaluated_systematic_preflight_failure",
            "observed_s": str(drift_decimal),
            "screen_s": str(screen),
            "maximum_budgetable_drift_s": str(maximum_drift),
        }
        return result, ("instrument_calibration_mismatch",)

    stale_triggers = [
        trigger
        for trigger in observed_triggers
        if trigger
        in {
            "protocol_or_estimator_byte_change",
            "corpus_doubles_from_19_to_38",
            "new_valid_same_identity_capture_expands_observed_range",
            "new_systematic_failure_challenges_preflight_screen",
        }
    ]
    if stale_triggers:
        result["acceptance"]["freshness"].update(
            {
                "status": "stale",
                "reason": "prospective_rederivation_required",
                "stale_triggers": stale_triggers,
            }
        )
        return result, ("calibration_acceptance_bound_stale",)

    excess = max(drift_decimal - screen, Decimal(0))
    drift_status = (
        "budget_exceeded"
        if drift_decimal > maximum_drift
        else "passed_budgeted"
        if drift_decimal > screen
        else "passed_screen"
    )
    result["acceptance"]["drift"] = {
        "status": drift_status,
        "observed_s": str(drift_decimal),
        "screen_s": str(screen),
        "excess_s": str(excess),
        "max_budgetable_excess_s": str(maximum_excess),
        "maximum_budgetable_drift_s": str(maximum_drift),
    }
    if drift_decimal > maximum_drift:
        return result, ("instrument_calibration_mismatch",)

    allowance = max(drift_decimal, screen)
    operative_bound = endpoint_max_decimal + allowance
    result.update(
        {
            "calibration_drift_allowance_s": float(allowance),
            "b_fiducial_s": float(operative_bound),
        }
    )
    result["acceptance"]["allowance"] = {
        "rule": "max(observed_drift_s,bracket_screen_s)",
        "value_s": str(allowance),
        "embedding_count": 1,
        "embedded_in": "b_fiducial_s",
        "endpoint_max_b_fiducial_s": str(endpoint_max_decimal),
        "operative_b_fiducial_decimal_s": str(operative_bound),
        "operative_b_fiducial_binary64_s": float(operative_bound),
    }
    result["status"] = "passed"
    return result, ()


def calibration_bracket_for_bundles(
    runs_root: Path,
    bundle_paths: Sequence[Path],
    policy: CalibrationBracketingPolicy,
    *,
    ledger_snapshot: CalibrationLedgerSnapshot | None = None,
    bracket_binding: Mapping[str, Any] | None = None,
    bracket_window_id: str | None = None,

codex
# U4 implementation plan — synthetic three-window live-ledger regression

## Baseline and constraints

Implement against U1 commit `f665dd4` (`impl/d117-u1-ledger-session` and the local `origin/…` ref both point there). A fresh remote lookup was impossible because network DNS is unavailable; no fetch was performed because this was explicitly read-only.

U4 remains logically downstream of U1 and U2. The non-successor portion can be prepared against U1; U4 must not merge with successor tests still skipped.

## Exact `WRITE_SCOPE`

Only:

- `tests/fixtures/calibration_live_three_window/fixture_spec.json`
- `tests/test_calibration_live_three_window.py`

No production modules, configuration, registry, bookkeeping, generated state, or existing tests are in scope.

## Fixture specification

`fixture_spec.json` will contain:

- Schema/version identifier for the U4 fixture.
- The expected production issued-anchor facts:
  - acceptance artifact SHA-256 `316113960c596a6f927987dbdf8f2bca4b0cca9ee4a59a540bbd32bba9048985`;
  - cutoff sequence `76`;
  - cutoff head `08456d5076c18a9a7f758969b02f5b6f7ad9fcc267dd12e2d3778c22458094d7`;
  - inventory `{valid: 30, systematic-invalid: 2, ordinary-invalid: 6}`.
- Exact six-field epoch copied from the issued artifact.
- One complete ten-field T1 vector:
  - `hardware_model`
  - `os_build`
  - `powermetrics_sha256`
  - `sampling_interval_ms`
  - `anchor_method_version`
  - `mlx_version`
  - `pulse_protocol_id`
  - `power_policy`
  - `estimator_revision`
  - `protocol_sha256`
- Three explicit window records: `alpha`, `beta`, `gamma`, each with unique session, window, plan, evidence-root, and runs-root suffixes.
- Window timing far enough apart to make causal/stale mutations unambiguous:
  - alpha science `[1_000_000, 1_000_100]`, endpoints `999_990/1_000_110`;
  - beta `[2_000_000, 2_000_100]`, endpoints `1_999_990/2_000_110`;
  - gamma `[3_000_000, 3_000_100]`, endpoints `2_999_990/3_000_110`.
- Endpoint decimal bounds below the issued range ceiling and with drift below the `0.010818` screen:
  - alpha `0.025/0.026`;
  - beta `0.027/0.028`;
  - gamma `0.029/0.030`.
- Expected capability/finalization sequences:
  - alpha `77/78/79`;
  - beta `80/81/82`;
  - gamma `83/84/85`.
- Expected candidate count `6`, imported candidate count `0`, final sequence `85`, and allowance literal `0.010818`.

Identifiers must be explicitly synthetic; they must not pre-empt U5–U7’s final campaign identifiers.

## Construction algorithm

`tests/test_calibration_live_three_window.py` will define a reusable `FixtureHarness`.

1. Load and byte-authenticate the checked-in issued acceptance artifact. Assert its exact SHA, sequence-76 cutoff, 38-member prior set, and 30/2/6 inventory.

2. Materialize 38 synthetic custody directories in a temporary checkout. Preserve the issued artifact’s attempt IDs and dispositions. Each directory gets deterministic:
   - `raw/powermetrics.plist`
   - `events.jsonl`
   - `power_trace.csv`
   - `instrument_evidence.json`
   - `manifest.json`

3. Build the historical disposition table and custody manifest, then call the public `prepare_historical_import`/`bootstrap_historical_import` path. Assert:
   - 76 receipts;
   - alternating historical reservation/finalization semantics;
   - 38 content-distinct observations;
   - 30 valid, two systematic-invalid, six ordinary-invalid;
   - every observation is import-marked;
   - the chain and generated sequence-76 head pin authenticate.

4. Construct a structurally valid synthetic issued acceptance artifact:
   - clone the production artifact’s policy/numeric fields;
   - bind its cutoff to the synthetic sequence-76 head;
   - replace the prior set with the 38 generated observations;
   - replace the 19 derivation-corpus identities/hashes with the first 19 generated valid members while retaining the original bound lexemes and arithmetic;
   - recompute `derivation_sha256`;
   - assert `_valid_acceptance_bound` before use.
   
   Patch only the acceptance-loader boundary to supply this artifact. Do not patch ledger loading, candidate discovery, binding validation, or bracket evaluation.

5. For each window, starting from the current pinned head:
   - call `append_bracket_session_receipt` with exactly two immutable slots;
   - call `finalize_bracket_session_slot` directly for `pre`, then `post`;
   - do not emit optional writer-claim receipts, preserving the memo’s three-receipt/session sequence model;
   - obtain the terminal pin through `terminal_head_pin_for_session`;
   - load a pinned snapshot with the sequence-76 baseline;
   - build the window binding with `build_calibration_bracket_binding`;
   - advance the synthetic committed pin before opening the next session.

6. After gamma, load exactly one immutable sequence-85 snapshot. Call `discover_calibration_candidates` once and reuse that exact six-candidate tuple and snapshot for all three evaluations.

7. Candidate custody remains fully hash-authenticated. Only the raw-physics refit is replaced with a deterministic test double returning each evidence file’s exact decimal bound; this keeps receipt, manifest, evidence, content-ID, epoch, T1, protocol, and path authentication live.

8. Structural mutation tests use a common `_rechain()` helper that recomputes sequence, predecessor, and receipt digests. This distinguishes semantic refusal from trivial broken-hash refusal.

## Named proof-obligation tests

| Test | Required proof |
|---|---|
| `test_issued_prefix_has_exact_76_receipt_38_observation_30_2_6_semantics` | Both the production anchor and generated prefix carry the ruled issuance shape. |
| `test_final_snapshot_discovers_exactly_six_live_and_zero_imported_candidates` | Six live candidates; no import-marked observation reaches candidate loading. |
| `test_alpha_beta_gamma_bind_only_their_own_pre_post_pairs` | Each binding resolves to its own two attempt/content/receipt digests. |
| `test_all_six_live_endpoints_are_same_epoch_causal_fresh_protocol_and_t1_valid` | Exact epoch/T1/protocol equality and causal/fresh timing for every endpoint. |
| `test_neighboring_endpoint_cannot_substitute_for_any_bound_endpoint` | Replacing either endpoint with any of the other five candidates refuses. |
| `test_all_three_verdicts_consume_same_complete_final_candidate_universe` | All verdicts pass only with the same final snapshot and complete six-candidate tuple; discovery occurs once. |
| `test_three_receipt_sessions_terminate_at_sequence_85` | Receipt events and sequences are exactly `76 + 3 × 3 = 85`. |
| `test_d110_never_zero_allowance_is_embedded_once_in_all_three_verdicts` | All three results record `max(drift, 0.010818)`, value `0.010818`, `embedding_count == 1`, and the correct operative decimal. |

## Named refusal-vector tests

### Import boundary

| Test | Setup and oracle |
|---|---|
| `test_import_marker_removal_refuses_authenticated_issuance_prefix` | Convert one fully re-chained import reservation/finalization pair to ordinary live events. Evaluation must refuse with `calibration_ledger_baseline_missing`. |
| `test_import_candidate_leakage_refuses_complete_universe_check` | Add a candidate derived from an import observation to the supplied tuple. Expect `calibration_ledger_off_ledger_artifact`. |
| `test_candidate_discovery_never_invokes_loader_for_import_marked_observations` | Spy on the observation-to-candidate loader; it must be called exactly six times, all after sequence 76. |

### Session/finalization integrity

| Test | Setup and oracle |
|---|---|
| `test_missing_session_or_finalization_receipt_refuses` | Subtests remove a capability, pre finalization, or post finalization and fully re-chain. Require session conflict/open refusal and no passing evaluation. |
| `test_duplicate_session_or_finalization_receipt_refuses` | Duplicate an open receipt and, separately, a finalization. Expect `calibration_ledger_bracket_session_conflict`. |
| `test_reordered_finalization_receipts_refuse` | Put post before pre and re-chain. Expect session conflict. |
| `test_conflicting_session_or_finalization_identity_refuses` | Change session identity, reserved attempt, custody, or plan hash on a later event and re-chain. Expect session conflict. |
| `test_open_session_refuses_claim_evaluation_and_terminal_pin` | Stop after a valid pre finalization. Snapshot contains `calibration_ledger_bracket_session_open`; terminal-pin creation and evaluation both refuse. |
| `test_abandoned_slot_without_governed_abort_refuses` | Finalize pre as abandoned but omit `abort_bracket_session`. The session remains open and cannot yield a terminal pin or candidate. |

### Head and chain authority

| Test | Setup and oracle |
|---|---|
| `test_physical_head_pin_mismatch_refuses` | Keep the pin at 76 while the physical chain reaches 85. Expect `calibration_ledger_head_mismatch`. |
| `test_rollback_from_pinned_terminal_head_refuses` | Pin sequence 85, truncate the physical chain to 84. Expect `calibration_ledger_rollback`. |
| `test_sibling_fork_refuses_even_when_pin_names_fork_tip` | Append a correctly hashed sibling transition and pin that tip. Expect `calibration_ledger_chain_conflict`. |
| `test_uncommitted_terminal_head_pin_refuses` | In a temporary Git repo, commit the sequence-76 pin, advance it to 85 without committing, and load with committed-pin enforcement. Expect `calibration_ledger_head_uncommitted`. |

### Complete observation universe

| Test | Setup and oracle |
|---|---|
| `test_omitted_registered_observation_refuses` | Remove one of six candidates from the supplied tuple. Expect `calibration_ledger_off_ledger_artifact`. |
| `test_added_registered_observation_invalidates_frozen_six_candidate_universe` | Append and pin a seventh authentic valid live observation, then supply the old six. Expect off-ledger refusal. |
| `test_duplicate_supplied_observation_refuses` | Duplicate one candidate while retaining tuple length. Expect off-ledger refusal from the duplicate/cardinality guard. |
| `test_off_ledger_observation_refuses` | Add a well-formed candidate with no receipt. Expect off-ledger refusal. |
| `test_content_substituted_observation_refuses` | Keep attempt/receipt identity but replace content or artifact hashes. Expect off-ledger refusal. |

### Binding integrity

| Test | Setup and oracle |
|---|---|
| `test_missing_bracket_binding_refuses` | Evaluate a session-backed window with no binding. Expect `calibration_bracket_binding_missing`. |
| `test_tampered_bracket_binding_refuses` | Alter an endpoint or identity without updating the binding digest. Expect `calibration_bracket_binding_invalid`. |
| `test_swapped_bracket_binding_endpoints_refuse` | Swap pre/post and recompute the outer digest. Exact role comparison must still reject it. |
| `test_cross_window_bracket_binding_refuses` | Supply alpha’s authentic binding to beta, and vice versa. Expect binding-invalid refusal. |

### Endpoint eligibility

| Test | Setup and oracle |
|---|---|
| `test_noncausal_bound_endpoint_refuses` | Move a bound pre after science start or post before science end; rebuild evidence and receipts. Expect bracket-missing/binding refusal, never neighbor substitution. |
| `test_stale_bound_endpoint_refuses` | Place a causal endpoint beyond `MAX_AGE_S`. Expect `instrument_calibration_stale`. |
| `test_t1_mismatched_bound_endpoint_refuses` | Make reservation, evidence, and receipt internally consistent under a different T1 value while science keeps the original T1. Expect `instrument_calibration_bracket_missing`. |
| `test_non_v3_protocol_endpoint_refuses` | Make one authentic endpoint v2 rather than the claim-bearing v3 protocol. Expect bracket-missing refusal. |
| `test_identity_epoch_mismatch_refuses` | Change one acceptance identity field in the evaluated science binding. Expect `calibration_acceptance_bound_stale` with that field listed. |
| `test_systematic_live_observation_refuses_under_prior_artifact` | Classify one live observation systematic-invalid. Expect stale/refusal and the systematic trigger; no successor is consulted. |

### D-102 triggers available under U1

| Test | Setup and oracle |
|---|---|
| `test_range_expanding_live_observation_refuses_prior_artifact_and_requires_successor` | Set one valid endpoint above `0.03355875667989999`. The prior artifact must become stale with `new_valid_same_identity_capture_expands_observed_range`. |
| `test_observation_count_at_38_refuses_prior_artifact_and_requires_successor` | Extend the base 30+6 valid inventory with two further authenticated valid same-epoch observations. At 38, require `corpus_doubles_from_19_to_38` and stale refusal. |

## Tests staged behind U2

Keep these methods in the same module to preserve the exact U4 write scope. While U2’s public API/design brief is unavailable, mark them with an explicit `unittest.skip` reason. Imports of U2 APIs must occur inside the skipped methods so the module remains importable.

Before U4 merges, U2 must land, the skips must be removed, and all five tests must pass:

- `test_range_expanding_live_observation_passes_only_with_authenticated_successor`
  - Judge the range expander under the prior artifact, stop before science, build/register a successor over the complete governed prefix, finalize the session, and prove the final bracket passes only under that successor.

- `test_count_boundary_passes_only_with_authenticated_successor`
  - Reach exactly 38 valid same-epoch observations, refuse the prior artifact, then prove a deterministic registered successor restores eligibility.

- `test_successor_cannot_absorb_systematic_observation_as_valid`
  - Attempt to include or relabel a systematic observation in the successor corpus. U2 must refuse; a successor cannot launder it.

- `test_successor_refuses_omitted_authenticated_prefix_observation`
  - Omit any import or finalized live observation at or before the successor cutoff, recompute otherwise self-consistent bytes, and require registry/validator refusal.

- `test_successor_refuses_changed_authenticated_prefix_observation`
  - Change content ID, disposition, epoch, attempt identity, or receipt/cutoff identity in the authenticated prefix and require refusal.

Use skip-marking rather than a separate module: a second module is outside the frozen U4 scope and makes it easier for the canonical suite to overlook the staged vectors. Skips are temporary branch state, not an acceptable merged U4 outcome.

## Verification

During pre-U2 staging:

```sh
python3 -m unittest tests.test_calibration_live_three_window
```

Expected: 38 active tests pass and exactly five U2-dependent tests skip.

After U2 lands:

```sh
python3 -m unittest tests.test_calibration_live_three_window
python3 -m unittest tests.test_calibration_live_three_window
python3 -m unittest discover -s tests
```

Acceptance:

- 43 U4 tests pass;
- zero U4 skips remain;
- two consecutive focused runs produce identical semantic receipts, bindings, successor bytes, and trigger outcomes for the same fixture root;
- canonical suite passes;
- no production or bookkeeping files changed.

## Estimated size

- `fixture_spec.json`: approximately 180–300 lines.
- Test harness and 43 tests: approximately 1,100–1,450 lines.
- Total: approximately 1,300–1,750 lines.
- Focused runtime target: under 20 seconds by constructing one pristine base tree per class and copying it for mutation tests.

## Risks and mitigations

- **Sequence-85 versus U1 claim receipts:** U1 added optional persistent slot-claim events. Exercising those through the production writer would yield five receipts per window and terminate at 91. This plan follows the memo’s explicit 85 oracle by calling the public open/finalize APIs directly. Existing U1 tests retain claim/concurrency coverage.
- **Synthetic acceptance authentication:** synthetic historical evidence cannot reproduce the off-repo production content hashes. U4 therefore validates the real issued artifact separately, then uses a structurally validated synthetic issued artifact at the loader boundary. All downstream ledger, custody, candidate, binding, and evaluation checks remain live.
- **Mutation tests becoming trivial:** every semantic mutation is re-chained and re-pinned unless the vector specifically targets hashes or heads.
- **Reason stacking:** tests assert the exact refusal when only one contract should fire; deliberately compound malformed cases assert the required primary taxonomy plus a failed verdict.
- **U2 API uncertainty:** successor semantics and oracles are frozen above, but the mechanical adapter cannot be completed until the U2 brief/public API lands.
- **Runtime from 44 custody trees:** build the pristine fixture once and copy it per test; do not regenerate all physics artifacts for every vector.

## Lead questions

1. Confirm that sequence 85 is the normative U4 oracle and that optional U1 slot-claim receipts are intentionally excluded from this semantic regression. Recommended: keep 85 here and add any claim-enabled production-path integration check under U1’s writer tests, not U4.
2. Ratify the successor corpus rule: all content-distinct, valid, same-epoch observations through the authenticated cutoff; systematic, ordinary-invalid, abandoned, unresolved, and duplicates remain recorded but excluded.
3. Confirm that U4 may use the structurally valid synthetic issued artifact described above rather than requiring the unavailable off-repo production ledger/custody bytes.
4. Decide whether the five temporary successor skips may exist on an intermediate U4 branch. Recommended: yes during staging, but never in the merged U4 commit.
5. Confirm `f665dd4` remains the intended U1 integration base, since a fresh origin lookup was unavailable in this read-only environment.
tokens used
148,569
# U4 implementation plan — synthetic three-window live-ledger regression

## Baseline and constraints

Implement against U1 commit `f665dd4` (`impl/d117-u1-ledger-session` and the local `origin/…` ref both point there). A fresh remote lookup was impossible because network DNS is unavailable; no fetch was performed because this was explicitly read-only.

U4 remains logically downstream of U1 and U2. The non-successor portion can be prepared against U1; U4 must not merge with successor tests still skipped.

## Exact `WRITE_SCOPE`

Only:

- `tests/fixtures/calibration_live_three_window/fixture_spec.json`
- `tests/test_calibration_live_three_window.py`

No production modules, configuration, registry, bookkeeping, generated state, or existing tests are in scope.

## Fixture specification

`fixture_spec.json` will contain:

- Schema/version identifier for the U4 fixture.
- The expected production issued-anchor facts:
  - acceptance artifact SHA-256 `316113960c596a6f927987dbdf8f2bca4b0cca9ee4a59a540bbd32bba9048985`;
  - cutoff sequence `76`;
  - cutoff head `08456d5076c18a9a7f758969b02f5b6f7ad9fcc267dd12e2d3778c22458094d7`;
  - inventory `{valid: 30, systematic-invalid: 2, ordinary-invalid: 6}`.
- Exact six-field epoch copied from the issued artifact.
- One complete ten-field T1 vector:
  - `hardware_model`
  - `os_build`
  - `powermetrics_sha256`
  - `sampling_interval_ms`
  - `anchor_method_version`
  - `mlx_version`
  - `pulse_protocol_id`
  - `power_policy`
  - `estimator_revision`
  - `protocol_sha256`
- Three explicit window records: `alpha`, `beta`, `gamma`, each with unique session, window, plan, evidence-root, and runs-root suffixes.
- Window timing far enough apart to make causal/stale mutations unambiguous:
  - alpha science `[1_000_000, 1_000_100]`, endpoints `999_990/1_000_110`;
  - beta `[2_000_000, 2_000_100]`, endpoints `1_999_990/2_000_110`;
  - gamma `[3_000_000, 3_000_100]`, endpoints `2_999_990/3_000_110`.
- Endpoint decimal bounds below the issued range ceiling and with drift below the `0.010818` screen:
  - alpha `0.025/0.026`;
  - beta `0.027/0.028`;
  - gamma `0.029/0.030`.
- Expected capability/finalization sequences:
  - alpha `77/78/79`;
  - beta `80/81/82`;
  - gamma `83/84/85`.
- Expected candidate count `6`, imported candidate count `0`, final sequence `85`, and allowance literal `0.010818`.

Identifiers must be explicitly synthetic; they must not pre-empt U5–U7’s final campaign identifiers.

## Construction algorithm

`tests/test_calibration_live_three_window.py` will define a reusable `FixtureHarness`.

1. Load and byte-authenticate the checked-in issued acceptance artifact. Assert its exact SHA, sequence-76 cutoff, 38-member prior set, and 30/2/6 inventory.

2. Materialize 38 synthetic custody directories in a temporary checkout. Preserve the issued artifact’s attempt IDs and dispositions. Each directory gets deterministic:
   - `raw/powermetrics.plist`
   - `events.jsonl`
   - `power_trace.csv`
   - `instrument_evidence.json`
   - `manifest.json`

3. Build the historical disposition table and custody manifest, then call the public `prepare_historical_import`/`bootstrap_historical_import` path. Assert:
   - 76 receipts;
   - alternating historical reservation/finalization semantics;
   - 38 content-distinct observations;
   - 30 valid, two systematic-invalid, six ordinary-invalid;
   - every observation is import-marked;
   - the chain and generated sequence-76 head pin authenticate.

4. Construct a structurally valid synthetic issued acceptance artifact:
   - clone the production artifact’s policy/numeric fields;
   - bind its cutoff to the synthetic sequence-76 head;
   - replace the prior set with the 38 generated observations;
   - replace the 19 derivation-corpus identities/hashes with the first 19 generated valid members while retaining the original bound lexemes and arithmetic;
   - recompute `derivation_sha256`;
   - assert `_valid_acceptance_bound` before use.
   
   Patch only the acceptance-loader boundary to supply this artifact. Do not patch ledger loading, candidate discovery, binding validation, or bracket evaluation.

5. For each window, starting from the current pinned head:
   - call `append_bracket_session_receipt` with exactly two immutable slots;
   - call `finalize_bracket_session_slot` directly for `pre`, then `post`;
   - do not emit optional writer-claim receipts, preserving the memo’s three-receipt/session sequence model;
   - obtain the terminal pin through `terminal_head_pin_for_session`;
   - load a pinned snapshot with the sequence-76 baseline;
   - build the window binding with `build_calibration_bracket_binding`;
   - advance the synthetic committed pin before opening the next session.

6. After gamma, load exactly one immutable sequence-85 snapshot. Call `discover_calibration_candidates` once and reuse that exact six-candidate tuple and snapshot for all three evaluations.

7. Candidate custody remains fully hash-authenticated. Only the raw-physics refit is replaced with a deterministic test double returning each evidence file’s exact decimal bound; this keeps receipt, manifest, evidence, content-ID, epoch, T1, protocol, and path authentication live.

8. Structural mutation tests use a common `_rechain()` helper that recomputes sequence, predecessor, and receipt digests. This distinguishes semantic refusal from trivial broken-hash refusal.

## Named proof-obligation tests

| Test | Required proof |
|---|---|
| `test_issued_prefix_has_exact_76_receipt_38_observation_30_2_6_semantics` | Both the production anchor and generated prefix carry the ruled issuance shape. |
| `test_final_snapshot_discovers_exactly_six_live_and_zero_imported_candidates` | Six live candidates; no import-marked observation reaches candidate loading. |
| `test_alpha_beta_gamma_bind_only_their_own_pre_post_pairs` | Each binding resolves to its own two attempt/content/receipt digests. |
| `test_all_six_live_endpoints_are_same_epoch_causal_fresh_protocol_and_t1_valid` | Exact epoch/T1/protocol equality and causal/fresh timing for every endpoint. |
| `test_neighboring_endpoint_cannot_substitute_for_any_bound_endpoint` | Replacing either endpoint with any of the other five candidates refuses. |
| `test_all_three_verdicts_consume_same_complete_final_candidate_universe` | All verdicts pass only with the same final snapshot and complete six-candidate tuple; discovery occurs once. |
| `test_three_receipt_sessions_terminate_at_sequence_85` | Receipt events and sequences are exactly `76 + 3 × 3 = 85`. |
| `test_d110_never_zero_allowance_is_embedded_once_in_all_three_verdicts` | All three results record `max(drift, 0.010818)`, value `0.010818`, `embedding_count == 1`, and the correct operative decimal. |

## Named refusal-vector tests

### Import boundary

| Test | Setup and oracle |
|---|---|
| `test_import_marker_removal_refuses_authenticated_issuance_prefix` | Convert one fully re-chained import reservation/finalization pair to ordinary live events. Evaluation must refuse with `calibration_ledger_baseline_missing`. |
| `test_import_candidate_leakage_refuses_complete_universe_check` | Add a candidate derived from an import observation to the supplied tuple. Expect `calibration_ledger_off_ledger_artifact`. |
| `test_candidate_discovery_never_invokes_loader_for_import_marked_observations` | Spy on the observation-to-candidate loader; it must be called exactly six times, all after sequence 76. |

### Session/finalization integrity

| Test | Setup and oracle |
|---|---|
| `test_missing_session_or_finalization_receipt_refuses` | Subtests remove a capability, pre finalization, or post finalization and fully re-chain. Require session conflict/open refusal and no passing evaluation. |
| `test_duplicate_session_or_finalization_receipt_refuses` | Duplicate an open receipt and, separately, a finalization. Expect `calibration_ledger_bracket_session_conflict`. |
| `test_reordered_finalization_receipts_refuse` | Put post before pre and re-chain. Expect session conflict. |
| `test_conflicting_session_or_finalization_identity_refuses` | Change session identity, reserved attempt, custody, or plan hash on a later event and re-chain. Expect session conflict. |
| `test_open_session_refuses_claim_evaluation_and_terminal_pin` | Stop after a valid pre finalization. Snapshot contains `calibration_ledger_bracket_session_open`; terminal-pin creation and evaluation both refuse. |
| `test_abandoned_slot_without_governed_abort_refuses` | Finalize pre as abandoned but omit `abort_bracket_session`. The session remains open and cannot yield a terminal pin or candidate. |

### Head and chain authority

| Test | Setup and oracle |
|---|---|
| `test_physical_head_pin_mismatch_refuses` | Keep the pin at 76 while the physical chain reaches 85. Expect `calibration_ledger_head_mismatch`. |
| `test_rollback_from_pinned_terminal_head_refuses` | Pin sequence 85, truncate the physical chain to 84. Expect `calibration_ledger_rollback`. |
| `test_sibling_fork_refuses_even_when_pin_names_fork_tip` | Append a correctly hashed sibling transition and pin that tip. Expect `calibration_ledger_chain_conflict`. |
| `test_uncommitted_terminal_head_pin_refuses` | In a temporary Git repo, commit the sequence-76 pin, advance it to 85 without committing, and load with committed-pin enforcement. Expect `calibration_ledger_head_uncommitted`. |

### Complete observation universe

| Test | Setup and oracle |
|---|---|
| `test_omitted_registered_observation_refuses` | Remove one of six candidates from the supplied tuple. Expect `calibration_ledger_off_ledger_artifact`. |
| `test_added_registered_observation_invalidates_frozen_six_candidate_universe` | Append and pin a seventh authentic valid live observation, then supply the old six. Expect off-ledger refusal. |
| `test_duplicate_supplied_observation_refuses` | Duplicate one candidate while retaining tuple length. Expect off-ledger refusal from the duplicate/cardinality guard. |
| `test_off_ledger_observation_refuses` | Add a well-formed candidate with no receipt. Expect off-ledger refusal. |
| `test_content_substituted_observation_refuses` | Keep attempt/receipt identity but replace content or artifact hashes. Expect off-ledger refusal. |

### Binding integrity

| Test | Setup and oracle |
|---|---|
| `test_missing_bracket_binding_refuses` | Evaluate a session-backed window with no binding. Expect `calibration_bracket_binding_missing`. |
| `test_tampered_bracket_binding_refuses` | Alter an endpoint or identity without updating the binding digest. Expect `calibration_bracket_binding_invalid`. |
| `test_swapped_bracket_binding_endpoints_refuse` | Swap pre/post and recompute the outer digest. Exact role comparison must still reject it. |
| `test_cross_window_bracket_binding_refuses` | Supply alpha’s authentic binding to beta, and vice versa. Expect binding-invalid refusal. |

### Endpoint eligibility

| Test | Setup and oracle |
|---|---|
| `test_noncausal_bound_endpoint_refuses` | Move a bound pre after science start or post before science end; rebuild evidence and receipts. Expect bracket-missing/binding refusal, never neighbor substitution. |
| `test_stale_bound_endpoint_refuses` | Place a causal endpoint beyond `MAX_AGE_S`. Expect `instrument_calibration_stale`. |
| `test_t1_mismatched_bound_endpoint_refuses` | Make reservation, evidence, and receipt internally consistent under a different T1 value while science keeps the original T1. Expect `instrument_calibration_bracket_missing`. |
| `test_non_v3_protocol_endpoint_refuses` | Make one authentic endpoint v2 rather than the claim-bearing v3 protocol. Expect bracket-missing refusal. |
| `test_identity_epoch_mismatch_refuses` | Change one acceptance identity field in the evaluated science binding. Expect `calibration_acceptance_bound_stale` with that field listed. |
| `test_systematic_live_observation_refuses_under_prior_artifact` | Classify one live observation systematic-invalid. Expect stale/refusal and the systematic trigger; no successor is consulted. |

### D-102 triggers available under U1

| Test | Setup and oracle |
|---|---|
| `test_range_expanding_live_observation_refuses_prior_artifact_and_requires_successor` | Set one valid endpoint above `0.03355875667989999`. The prior artifact must become stale with `new_valid_same_identity_capture_expands_observed_range`. |
| `test_observation_count_at_38_refuses_prior_artifact_and_requires_successor` | Extend the base 30+6 valid inventory with two further authenticated valid same-epoch observations. At 38, require `corpus_doubles_from_19_to_38` and stale refusal. |

## Tests staged behind U2

Keep these methods in the same module to preserve the exact U4 write scope. While U2’s public API/design brief is unavailable, mark them with an explicit `unittest.skip` reason. Imports of U2 APIs must occur inside the skipped methods so the module remains importable.

Before U4 merges, U2 must land, the skips must be removed, and all five tests must pass:

- `test_range_expanding_live_observation_passes_only_with_authenticated_successor`
  - Judge the range expander under the prior artifact, stop before science, build/register a successor over the complete governed prefix, finalize the session, and prove the final bracket passes only under that successor.

- `test_count_boundary_passes_only_with_authenticated_successor`
  - Reach exactly 38 valid same-epoch observations, refuse the prior artifact, then prove a deterministic registered successor restores eligibility.

- `test_successor_cannot_absorb_systematic_observation_as_valid`
  - Attempt to include or relabel a systematic observation in the successor corpus. U2 must refuse; a successor cannot launder it.

- `test_successor_refuses_omitted_authenticated_prefix_observation`
  - Omit any import or finalized live observation at or before the successor cutoff, recompute otherwise self-consistent bytes, and require registry/validator refusal.

- `test_successor_refuses_changed_authenticated_prefix_observation`
  - Change content ID, disposition, epoch, attempt identity, or receipt/cutoff identity in the authenticated prefix and require refusal.

Use skip-marking rather than a separate module: a second module is outside the frozen U4 scope and makes it easier for the canonical suite to overlook the staged vectors. Skips are temporary branch state, not an acceptable merged U4 outcome.

## Verification

During pre-U2 staging:

```sh
python3 -m unittest tests.test_calibration_live_three_window
```

Expected: 38 active tests pass and exactly five U2-dependent tests skip.

After U2 lands:

```sh
python3 -m unittest tests.test_calibration_live_three_window
python3 -m unittest tests.test_calibration_live_three_window
python3 -m unittest discover -s tests
```

Acceptance:

- 43 U4 tests pass;
- zero U4 skips remain;
- two consecutive focused runs produce identical semantic receipts, bindings, successor bytes, and trigger outcomes for the same fixture root;
- canonical suite passes;
- no production or bookkeeping files changed.

## Estimated size

- `fixture_spec.json`: approximately 180–300 lines.
- Test harness and 43 tests: approximately 1,100–1,450 lines.
- Total: approximately 1,300–1,750 lines.
- Focused runtime target: under 20 seconds by constructing one pristine base tree per class and copying it for mutation tests.

## Risks and mitigations

- **Sequence-85 versus U1 claim receipts:** U1 added optional persistent slot-claim events. Exercising those through the production writer would yield five receipts per window and terminate at 91. This plan follows the memo’s explicit 85 oracle by calling the public open/finalize APIs directly. Existing U1 tests retain claim/concurrency coverage.
- **Synthetic acceptance authentication:** synthetic historical evidence cannot reproduce the off-repo production content hashes. U4 therefore validates the real issued artifact separately, then uses a structurally validated synthetic issued artifact at the loader boundary. All downstream ledger, custody, candidate, binding, and evaluation checks remain live.
- **Mutation tests becoming trivial:** every semantic mutation is re-chained and re-pinned unless the vector specifically targets hashes or heads.
- **Reason stacking:** tests assert the exact refusal when only one contract should fire; deliberately compound malformed cases assert the required primary taxonomy plus a failed verdict.
- **U2 API uncertainty:** successor semantics and oracles are frozen above, but the mechanical adapter cannot be completed until the U2 brief/public API lands.
- **Runtime from 44 custody trees:** build the pristine fixture once and copy it per test; do not regenerate all physics artifacts for every vector.

## Lead questions

1. Confirm that sequence 85 is the normative U4 oracle and that optional U1 slot-claim receipts are intentionally excluded from this semantic regression. Recommended: keep 85 here and add any claim-enabled production-path integration check under U1’s writer tests, not U4.
2. Ratify the successor corpus rule: all content-distinct, valid, same-epoch observations through the authenticated cutoff; systematic, ordinary-invalid, abandoned, unresolved, and duplicates remain recorded but excluded.
3. Confirm that U4 may use the structurally valid synthetic issued artifact described above rather than requiring the unavailable off-repo production ledger/custody bytes.
4. Decide whether the five temporary successor skips may exist on an intermediate U4 branch. Recommended: yes during staging, but never in the merged U4 commit.
5. Confirm `f665dd4` remains the intended U1 integration base, since a fresh origin lookup was unavailable in this read-only environment.
