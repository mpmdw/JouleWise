# JouleWise Run State

Last updated: 2026-07-17 (WINDOW A OPEN — P2-038 LIVE TAIL CLOSED:
production_uncertainty_v1 PASSED on merged main (drain fixes PR #72/#74
after two live-bundle triage rounds; canonical record
runs/window_a_shakedown_final, pinned in detection_floor.md). AXI-SC
landed (PR #73): structured negative verdict, spec-decode Mac leg not
minted on pinned mlx-lm; DSpark/DFlash identified with MLX
implementations (extension-axes evaluation persisted). P2-015-SMOKE is
the quiet-Mac head, then P2-015 floors; overnight measurement program
in progress for Ed's advisor meeting. Session record:
`docs/run_reports/2026-07-16-resumption-nohw-batch.md` (+ tonight's
report to follow).)

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
   After any session that changed front-facing state, refresh
   `docs/site/DRIFT.md` (site-drift report) instead of deploying:
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

Source of truth for work selection: [state kernel](docs/process/state_kernel.json) (updated 2026-07-17). Latest report: [Resumption + no-hardware batch: PRs #67/#68/#69 merged, AXI-SB supported verdict, kernel closures](docs/run_reports/2026-07-16-resumption-nohw-batch.md).

### [ED-EXTERNAL]

- READY — E1 `P1-008`: Map phases to the academic calendar and capture the evaluator acceptance bar (minimum figures, demo expectation, reproducibility threshold, Mac-only plus split-deferral acceptability).

### [QUIET-MAC]

- READY — Q0 `P2-015-SMOKE`: Pre-Window-A tasks-sampler overhead smoke plus production-shaped campaign shakedown through doctor, strict validation, reducer 0.4.2, strict revalidation, campaign verdict split, and approved backup.

### [AGENT]

- READY — A4 `AXI-SB-ADAPTER`: Implement the static-batch Mac adapter follow-on minted by the AXI-SB supported verdict: batch_size configuration knob, per-sequence request-scoped token events per the AXI-SA contract, realized-vs-configured batch recording, and structured memory-fit outcomes, with strict-valid mock or smoke bundles and no energy claims.

<!-- END GENERATED: state-kernel run-state-intake -->

## Superseded stop card (C-028)

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

## Session History (pointers only — run reports own the narrative)

Parenthetical states below are historical at each report's head; they are not
current restart instructions. Current state is the C-028 block above.

- 2026-07-13 Bridge v1: bridge-protocol/v1 contract + scripts/bridge tooling
  (PR #64; co-designed with Sol over the bridge itself):
  `docs/run_reports/2026-07-13-bridge-v1.md`
- 2026-07-13 Restart close: #61-#63 merged at delta-audited heads
  (DRA-001 fixed; XSI-1 CI hardening), site live under cap; audit gate
  declared: `docs/run_reports/2026-07-13-restart-merge-deploy.md`
- 2026-07-12 Claude↔Sol bidirectional bridge (concurrent Ed-directed
  thread; lead-verified 2026-07-13):
  `docs/run_reports/2026-07-12-claude-sol-bridge.md`
- 2026-07-12 Agent-lane triple: SITE-01/P2-049/P2-028 → PRs #61-#63 at
  lead-gated heads; delta re-audits owed pre-merge on #62/#63:
  `docs/run_reports/2026-07-12-agent-lane-triple.md`
- 2026-07-11 P2-041 vetted rebuild (uncommitted; lead pathspec review and
  commit pending): `docs/run_reports/2026-07-11-p2041-vetted-rebuild.md`

- 2026-07-10 NV-GATE-2 idle-capture regression debug/fix (uncommitted;
  localhost re-verification remains lead-gated):
  `docs/run_reports/2026-07-10-nvgate2-idle-capture-fix.md`
- 2026-07-10 NV-GATE-2 CODE-NOW implementation (NV-1/NV-3/NV-4/NV-5;
  live promotion evidence still gated):
  `docs/run_reports/2026-07-10-nvgate2-codenow.md`
- 2026-07-10 NV-GATE-2 accepted-findings fix round (uncommitted; merge
  metadata recreation and lead gate pending):
  `docs/run_reports/2026-07-10-nvgate2-fix-round.md`
- 2026-07-10 P2-038 accepted-findings fix round (all FIX-1..FIX-6 green;
  content-merged `origin/main`, Git merge metadata sandbox-blocked):
  `docs/run_reports/2026-07-10-p2038-fix-round.md`
- 2026-07-10 P2-038 production uncertainty software path (live quiet-machine
  closure still open):
  `docs/run_reports/2026-07-10-p2038-production-uncertainty.md`
- 2026-07-10 P2-040 reducer-version compatibility review fix (uncommitted):
  `docs/run_reports/2026-07-10-p2040-versioning-fix.md`
- 2026-07-10 P2-040 remainder implementation (uncommitted, pending lead
  pathspec commit/corpus gate):
  `docs/run_reports/2026-07-10-p2040-remainder.md`
- 2026-07-10 P2-040 / RETRO-001 fix round (committed on c027-int-p2040
  after lead review): `docs/run_reports/2026-07-10-p2040-fix-round.md`
- 2026-07-09 C-027 whole-project council review (7 gpt-5.6-sol lenses +
  counterreview + independent final examiner):
  `docs/reviews/2026-07-09-c027-whole-project-review.md` (compact run
  report: `docs/run_reports/2026-07-09-c027-council-review.md`)
- 2026-07-09 Claude Code → Codex MCP bridge hardening and live smoke:
  `docs/run_reports/2026-07-09-claude-codex-mcp-bridge.md`
- 2026-07-12 adaptive Claude Code ↔ Sol/Fable bridge follow-up:
  `docs/run_reports/2026-07-12-claude-sol-bridge.md`
- 2026-07-09 P2-034 broad campaign packs (C-026; PR #39):
  `docs/run_reports/2026-07-09-p2034-broad-packs.md`
- 2026-07-09 spec-fleshing wave 2, ultracode (C-025; PRs #33..#38;
  D-056..D-059): `docs/run_reports/2026-07-09-spec-fleshing-wave2.md`
- 2026-07-09 spec-fleshing wave 1 (C-024; PRs #29..#32; D-052..D-055):
  `docs/run_reports/2026-07-09-spec-fleshing-wave1.md`
- 2026-07-09 scientific-rigor review of suite/benchmark/question bank
  (C-023; review-only; full record in
  `docs/reviews/2026-07-09-scientific-rigor-review.md`):
  `docs/run_reports/2026-07-09-scientific-rigor-review.md`
- 2026-07-09 CP-5 resume: pre-campaign review completed, stop card
  cleared, PRs #22..#28 merged, Window-A GO
  (C-022): `docs/run_reports/2026-07-09-cp5-resume.md`
- 2026-07-09 meta-process stop-card + codex-bridge audit cleanup
  (D-050; CP-5 preserved untouched):
  `docs/run_reports/2026-07-09-meta-process-stop-card-cleanup.md`
- 2026-07-09 advisor status-site live-depth refresh (D-051/C-021;
  subordinate to the then-active CP-5 stop card):
  `docs/run_reports/2026-07-09-advisor-status-site.md`
- 2026-07-08 suite build (C-017; adjudication + PRs #17/#18/#20/#19;
  D-044..D-047): `docs/run_reports/2026-07-08-suite-build.md`
- 2026-07-08 suite-science + expansion (C-014/C-015; PRs #14/#15/#16;
  D-038..D-042): `docs/run_reports/2026-07-08-suite-science-expansion.md`
- 2026-07-08 Lakebed deploy (C-013):
  `docs/run_reports/2026-07-08-lakebed-deploy.md`
- 2026-07-08 site observatory (PR #13):
  `docs/run_reports/2026-07-08-site-observatory.md`
- 2026-07-08 critique second-pass + councils+critique (C-011 → PR #12):
  `docs/run_reports/2026-07-08-councils-critique-session.md`
- 2026-07-07/08 resume+merge (C-009 first full run; PRs #8..#11):
  `docs/run_reports/2026-07-07-resume-merge-session.md`
- Older: see `docs/run_reports/` (dated files).

## Current Verification

- PR #65 branch `impl/bridge-v1.1` final head `8b96bd4`: canonical
  `Ran 1387 tests`, `OK (skipped=10)`, lead-run 2026-07-13 (four
  lead-side full-suite runs across the fix arc: 1371→1381→1385→1387);
  CI green on the final head (build, installed-wheel, tests 3.11 +
  3.14); `scripts/check-codex-mcp.mjs` 5/5 PASS with the v1.1 adapter;
  live session-open/close and reverse-consult probes recorded in
  `docs/run_reports/2026-07-13-bridge-v11.md`.
- Merged main `d285989` (post #65): canonical `Ran 1387 tests`, `OK
  (skipped=10)`, lead-run 2026-07-13 on the merged head;
  `scripts/check-codex-mcp.mjs` all PASS; no active workspace leases.
- Previous session (post #61-#63 merges + bridge v1 landing, pre-commit
  head `99b8640`): canonical `Ran 1318 tests in 111.017s`, `OK
  (skipped=10)`, lead-run 2026-07-13; bridge protocol checker 8/8 PASS;
  bridge focused tests 4/4 OK. Merged-main backstop at `12131b0` was
  `Ran 1314 tests`, `OK (skipped=10)`. Live capsule: measured artifact
  854,349 B deployed, routes 5/5 HTTP 200, freshness 14/14 current at
  `7d3ea57`.
- Prior head `main@194ea39` (post #59 + #60 merges): canonical `Ran 1258
  tests`, `OK (skipped=10)`, lead-run 2026-07-11 fresh-thread intake.
  PRs #41-#60 are all merged.
- Prior head `main@cc3afc3`: canonical `Ran 1220 tests`, `OK (skipped=10)`;
  retained corpus strict gate 6/6; PR #59 pre-merge lead replay was
  `Ran 1224 tests`, `OK (skipped=12)`.
- Count convention for C-028 records: ordinary worktree replays report
  `skipped=12`, final main reports `skipped=10`, and restricted managed
  sandboxes may report `skipped=13` when their environment-gated probe is
  unavailable. Preserve those environment labels when citing a tail.

### Historical verification archive (exact at the recorded heads)

- P2-041 vetted rebuild: baseline canonical `Ran 1041 tests in 67.995s`,
  `OK (skipped=13)`; final focused recipe modules `Ran 398 tests in 54.964s`,
  `OK (skipped=1)`; final canonical `Ran 1062 tests in 76.436s`, `OK
  (skipped=13)`; `git diff --check` and the dead-private-helper search clean.
  The retained corpus and localhost socket gates skipped loudly; no live or
  quiet-Mac validation was claimed. Report:
  `docs/run_reports/2026-07-11-p2041-vetted-rebuild.md`.

- PR #49 P2-038 rail-only flake: pre-fix exact-test loop failed 4/100;
  retained failure emitted `cadence_ratio_unrecorded` plus
  `interpolation_bound_unrecorded` because the final trace sample preceded the
  stop marker. Archived `origin/main` reproduced on iteration 6. The
  fixture-only terminal-sample handshake fix passed the exact test 100/100,
  focused module `Ran 5 tests in 30.480s`, `OK`, and canonical suite
  `Ran 1041 tests in 66.509s`, `OK (skipped=13)`. Report:
  `docs/run_reports/2026-07-10-pr49-p2038-flake-root-cause.md`.
- NV-GATE-2 idle-capture regression fix: historic fake-sampler plus new
  delayed-readiness regression passed together in 3 consecutive fresh
  processes; canonical suite `Ran 1023 tests in 35.164s`, `OK (skipped=13)`;
  `py_compile` and `git diff --check` clean. The exact localhost contract was
  attempted 3 times but loudly skipped before worker execution because this
  sandbox denied socket bind; lead socket-capable 3x rerun remains required.
  Report: `docs/run_reports/2026-07-10-nvgate2-idle-capture-fix.md`.
- NV-GATE-2 accepted-findings fix round: focused node-worker/subprocess,
  controller, reducer, strict-dispatch, and schema surface `Ran 229 tests in
  4.995s`, `OK (skipped=2)`; the historic fake-sampler test passed three
  consecutive fresh-process runs; canonical suite `Ran 1022 tests in 34.406s`,
  `OK (skipped=13)`; targeted `py_compile` and `git diff --check` clean. The
  0.3.1 dispatch came from `origin/impl/p2040-remainder` because post-main did
  not contain it. Report: `docs/run_reports/2026-07-10-nvgate2-fix-round.md`.
- NV-GATE-2 CODE-NOW worktree: baseline `Ran 910 tests in 32.549s`,
  `OK (skipped=12)`; final canonical suite `Ran 922 tests in 33.551s`,
  `OK (skipped=13)`; focused NV-1/NV-3/NV-4/NV-5 surface `Ran 232 tests
  in 6.085s`, `OK (skipped=2)`; `git diff --check` and targeted
  `py_compile` clean. The added skip is loud and specific: this managed
  sandbox denied localhost socket bind for NV-5. No live NVIDIA evidence or
  de-provisionalization was claimed.
- P2-038 accepted-findings fix round: all FIX-1..FIX-6 complete; focused
  `Ran 70 tests in 41.211s`, `OK`; canonical `Ran 992 tests in 68.140s`,
  `OK (skipped=12)`; `git diff --check` clean. The real-child rail-only path
  now withholds drift on unknown contamination while gross remains eligible;
  P2-039's pending guard validator accepts the emitted block; backup launch
  failure, extreme-sentinel exclusion, child invocation, and literal phase
  constants are regression-tested. The absent worktree `runs/` corpus produced
  the loud six-bundle acceptance-gate skip. Git merge metadata remains absent
  because the managed sandbox cannot write the external worktree admin dir;
  the exact clean three-way `origin/main` content snapshot is applied.
- P2-040 reducer-version review fix: focused strict/reducer run
  `Ran 84 tests in 1.908s`, `OK`; extended strict/reducer/schema run
  `Ran 104 tests in 1.997s`, `OK (skipped=1)`. Canonical run reached
  `Ran 926 tests in 33.732s`, `FAILED (failures=1, skipped=12)` solely at
  pre-existing `test_telemetry_measure_idle_with_fake_nvidia_smi`; isolated
  reruns reproduce its 0.2-second fake-process timing failure. All
  reducer/version tests pass; no out-of-scope node-worker change was made.
- P2-040 remainder worktree: pre-change baseline `Ran 910 tests in 34.584s`,
  `OK (skipped=12)`; post-change focused affected modules `Ran 256 tests in
  3.744s`, `OK (skipped=1)`; canonical `Ran 924 tests in 32.812s`, `OK
  (skipped=12)`; compileall and `git diff --check` clean. The unchanged
  six-corpus test produced its required loud skip because `runs/` is absent;
  lead 6/6 strict read-only rerun remains the landing gate.
- P2-042 emitter branch `impl/p2042` (lead-committed base; draft PR #46;
  targeted-review fix round complete in the worktree, no fix-round commit):
  FIX-1 fail-closed typed identity/linkage validation, FIX-2 semantic
  `run_id` derivation, and FIX-3 raw-byte AP hashing/LF config emission are
  implemented. Focused manifest/generator/campaign checks: `Ran 82 tests in
  12.317s, OK`; final canonical suite: `Ran 989 tests in 33.405s, OK
  (skipped=12)`. Review regressions cover `run_id=[]`, one malformed identity
  at each manifest object layer, a fully rehashed coherent rename, and a CRLF
  AP fixture. Report:
  `docs/run_reports/2026-07-10-p2042-analysis-manifest.md`.
- P2-040 reducer-version review fix: focused strict/reducer run
  `Ran 84 tests in 1.908s`, `OK`; extended strict/reducer/schema run
  `Ran 104 tests in 1.997s`, `OK (skipped=1)`. Canonical run reached
  `Ran 926 tests in 33.732s`, `FAILED (failures=1, skipped=12)` solely at
  pre-existing `test_telemetry_measure_idle_with_fake_nvidia_smi`; isolated
  reruns reproduce its 0.2-second fake-process timing failure. All
  reducer/version tests pass; no out-of-scope node-worker change was made.
- P2-040 remainder worktree: pre-change baseline `Ran 910 tests in 34.584s`,
  `OK (skipped=12)`; post-change focused affected modules `Ran 256 tests in
  3.744s`, `OK (skipped=1)`; canonical `Ran 924 tests in 32.812s`, `OK
  (skipped=12)`; compileall and `git diff --check` clean. The unchanged
  six-corpus test produced its required loud skip because `runs/` is absent;
  lead 6/6 strict read-only rerun remains the landing gate.
- P2-040 / RETRO-001 fix-round worktree: canonical suite `Ran 908 tests in
  32.723s`, `OK (skipped=11)`; focused 211 tests OK; claims lint exit 0 with
  no errors; `git diff --check` clean. The absent `runs/` corpus produced the
  required loud six-bundle acceptance-gate skip; the lead corpus gate then
  PASSED (6/6 strict via corpus symlink), plus mock e2e run+strict+reduce
  and the post-merge full suite (OK, skipped=12).
- Claude Code 2.1.207, Codex CLI 0.144.0, and Node 23.7.0 pass the
  bidirectional protocol checker. Claude → Sol now uses `gpt-5.6-sol` with
  `high` fallback/default and task-triggered xhigh/ultra escalation; the
  final guarded `/codex` smoke returned `JOULEWISE_SOL_HIGH_GUARDED_OK`
  (thread `019f5a2a-2f4a-7b33-8a6d-b44dcc5a7a26`) with source `mcp`, effort
  `high`, read-only sandbox, and `on-request` approvals. Claude-originated
  Sol sessions disable the reverse server. Top-level Sol → Fable uses the
  sole `consult_fable` MCP tool; live token `JOULEWISE_FABLE_MCP_OK` on
  thread `019f5a26-d8a6-7993-b48d-8131d88748b9`. Focused bridge tests pass
  4/4 and `gen_state.py --check` passes. The current full suite ran 1,317
  tests but is not green: one failure + one error in `test_gen_state` are
  caused by the concurrent uncommitted state-kernel removal of `P2-028`
  while the existing fidelity tests still require that ID; bridge tests are
  unaffected. Full details: `docs/run_reports/2026-07-12-claude-sol-bridge.md`.
- Last code-bearing verified head c095c83 (post PR #39; note: 36d5641
  later changed `scripts/build_site.py` on main without a recorded
  verification — flagged by C-027, covered by RETRO-001): suite `OK (skipped=10)` and
  repo lint errors=0, lead-run; pack lint errors=0 warnings=0.
- Prior: main after wave-2 integration fixes: `python3 -m unittest discover -s
  tests` → `Ran 877 tests, OK (skipped=10)`, lead-run; repo lint
  errors=0; CI green on all six PR heads (#33..#38); combined-ref
  pre-merge suite check green; live rotated mock campaign strict-valid
  with order provenance (lead-validated); mock e2e emits uncertainty
  fields per D-057.
- Prior: series head f75134d (post PRs #29..#32; docs-only) lead-verified;
  integration-fix commit 7156295 is also docs-only (no test surface):
  `python3 -m unittest discover -s tests` → `Ran 822 tests, OK
  (skipped=10)`, lead-run; CI green on all four PR heads (py3.11+py3.14);
  integration reviewer independently re-ran the suite and recomputed the
  detection-floor campaign arithmetic.
- Prior verification (7666652, post PRs #22..#28): `Ran 822 tests, OK
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

- Main checkout is at the post-#65 merge with the regenerated baked
  site and merged-state bookkeeping committed straight to main per
  convention; the tree is clean after the site-regen commit. Merged
  bridge branches were deleted local+origin. One stale nested worktree
  (`.claude/worktrees/magical-jones-79e5f4`, detached, clean) was
  removed this session; the long-lived `JouleWise-wt/*` stream worktrees
  are untouched. The Lakebed upload was completed by Ed and
  lead-verified live; no pending actions remain.
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
