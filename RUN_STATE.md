# JouleWise Run State

Last updated: 2026-07-08 (suite BUILD close + alignment fix PR #21 +
meta-reassessment; adjudication D-044..D-047; PRs #17..#21 merged;
suite 734; C-017/C-018/C-019)

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

At the end of substantial work:

1. Update this file with what changed.
2. Update `TASK_QUEUE.md` with completed, added, or re-ranked tasks.
3. Add or update a detailed report in `docs/run_reports/`.
4. Record tests, commands, blockers, and the next best task.
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
   After any session that changed front-facing docs, REGENERATE and
   REDEPLOY the site so the public snapshot tracks the repo (C-012):
   `python3 scripts/build_site.py && python3 scripts/pack_capsule.py &&
   (cd site_capsule && npx lakebed deploy)`.
9. Call out any dirty working-tree state that should not be accidentally
   committed.

## Current Project Status

**Suite BUILD session COMPLETE and MERGED (2026-07-08; C-017;
D-044..D-047).** The workload suite is now CODE, not contracts: P2-010a
generic substrate (PR #17: suite.py, run_suite protocol, mock+MLX
execution, BundleReader suite validation, reducer suite_metrics, strict
rollup provenance), P2-010b affine core + smoke manifest (PR #18,
promoted via #20 after a base-retarget slip), P2-012 phase-1 + P2-020
generator engine (PR #19: gensuite, six categories + five ids-native
sentinels). All 37 research-doc amendments adjudicated first (recorded
dispositions). Live-verified on real MLX at three code states; three
live-only defects caught and fixed at the lead gate. Post-merge
integration review: zero cross-stream defects.

**RESTART HERE (next agent):**
1. Read `docs/run_reports/2026-07-08-suite-build.md` (session record +
   restart detail).
2. **Suite follow-ons [AGENT]:** envelope-gate analysis script (queue
   P2-010 row), lead-side real-tokenizer manifest generation (P2-012
   row), campaign-runner text-item hash check (P2-025).
3. **Quiet Window A [QUIET-MAC], next machine-quiet opportunity:**
   P2-015 expanded floors FIRST (incl. lead-run tasks-sampler + settle
   smoke), then P2-006 2M with drift sentinels; fail-closed runner +
   order manifest; claims per `docs/contracts/claims_ladder.md` +
   `docs/contracts/analysis_plans.md`; no-agent quiet lock (C-009 T5);
   corpus backed up per R-016. The affine smoke campaign (B=5,
   ~10-25 min) may ride a quiet-window tail after P2-015.
4. Window B (P2-019 q4 grid + P2-020 campaign) with n sized from A.

## Session History (pointers only — run reports own the narrative)

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

- Merged main (49c5b66 + reassessment batch): `python3 -m unittest
  discover -s tests` → `Ran 734 tests, OK (skipped=10)` (post PRs
  #17..#21; #21 = D-013 alignment-capture window fix, C-018).
- Live lead gates on merged main: real MLX (1.5B, mock telemetry) suite
  bundle strict-valid + reduced (sampler pinned via sample_utils; honest
  per-item identifiability); mock affine smoke 26/26 strict-valid.
- CI green on both matrix legs on every PR head and post-review commit.
- `validate-bundle --strict` green over all 6 real corpus bundles
  (unchanged this session; the lead-gate suite bundles are disposable
  /tmp artifacts, not corpus).
- Post-merge integration review: no cross-stream defects; AP-6
  vocabulary join verified; repeated-seed drift test green.

## Known Workspace State

- `main` is pushed and current (through this session's bookkeeping).
- Worktrees `jw-wt-suite`, `jw-wt-affine`, `jw-wt-gens` may remain
  (branches merged; safe to remove with `git worktree remove`).
- `/tmp/jw-lead-verify/` holds disposable lead-verification artifacts.

## What Is Next

Follow `TASK_QUEUE.md` (lane-annotated). In order:

1. **P2-015 then P2-006 in quiet Window A** [QUIET-MAC] (unchanged top;
   affine smoke campaign may ride the window tail).
2. **Suite follow-ons** [AGENT]: envelope-gate script; real-tokenizer
   manifest generation; P2-025 runner hash check.
3. **Ed's external one-pass** [ED-EXTERNAL]: calendar, device access,
   borrow window, wall meter, backup destination (P0-003).
4. **3.0.2 llama.cpp spike** [AGENT after R-003 approval].

Hardware-gated (unchanged): 2K/2L (P1-006), wall meter (P1-003),
topology (P1-004), calendar mapping (P1-008).

## Open Decisions And Blockers

- Supervisor approval and scope pending (P1-001, R-001 — mitigation
  holding); gates FULL D-016 closure.
- Real backup destination pending (P0-003; interim same-disk active).
- Calendar dates pending (P1-008, R-012).
- Wall-meter decision pending (P1-003, R-007).
- Physical network topology pending (P1-004, R-011).
- NVIDIA/Orin access evidence pending (P1-006; gates 2K/2L).
- Git author identity on this machine auto-selected as
  `Ed R <edr@Eds-MacBook-Pro.local>`. Amend future commits if a
  different identity is needed.
