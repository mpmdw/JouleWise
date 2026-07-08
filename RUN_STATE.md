# JouleWise Run State

Last updated: 2026-07-08 (suite-science + expansion session close; PRs
#14/#15/#16 merged; suite 617; site redeployed against this checkpoint)

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

**Suite-science + expansion session COMPLETE and MERGED (2026-07-08;
C-014/C-015; D-038..D-042).** Three PRs landed: #14 (analysis-plans
contract; program v2 with the Q4 L3 grid + comparative-MDE floors; suite
architecture v2 + benchmark interop + capability map; the suite
implementation research handoff), #15 (P2-021 drift sentinels — DONE),
#16 (Window-A capture set — the 2M corpus will carry its covariates:
per-run env snapshots, cooldown traces, inter-run gaps, tokenize/setup
phases, memory snapshots, sampler metadata). A sacred-window blocker
(in-window run_end memory snapshot) was caught by the review stack and
fixed pre-merge; the AP-4 equivalence gate was corrected pre-merge
(margin-clears-floor). Post-merge integration review: zero cross-stream
defects; live two-model matrix + sentinel campaign subset verified.

**RESTART HERE (next agent):**
1. Read `docs/run_reports/2026-07-08-suite-science-expansion.md` (the
   session record incl. restart detail), then
   `docs/phase_2/suite_implementation_research.md`.
2. **Suite build [AGENT], UNBLOCKED (D-042):** adjudicate the research
   doc's cross-check amendments (recorded dispositions), then implement
   P2-010a generic substrate → P2-010b smoke ladder → P2-012 phase-1
   generators + P2-020 sentinel content. Full review tier
   (measurement-semantics). This is the top agent-lane task.
3. **Quiet Window A [QUIET-MAC], next machine-quiet opportunity:**
   P2-015 expanded floors FIRST (incl. lead-run tasks-sampler + settle
   smoke), then P2-006 2M with drift sentinels; fail-closed runner +
   order manifest; claims per `docs/contracts/claims_ladder.md` +
   `docs/contracts/analysis_plans.md`; no-agent quiet lock (C-009 T5);
   corpus backed up per R-016.
4. Window B (P2-019 q4 grid + P2-020 campaign) with n sized from A.

## Session History (pointers only — run reports own the narrative)

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

- Merged main (fcd111a): `python3 -m unittest discover -s tests` →
  `Ran 617 tests, OK (skipped=10)` (as of 2026-07-08, post PRs #14..#16).
- `validate-bundle --strict` green over all 6 real corpus bundles under
  the merged capture code, read-only, unrewritten.
- Live lead gate on the capture head: real MLX (1.5B, mock telemetry)
  strict-valid bundle with the new evidence fields populated and honest
  (display 1/0 with pipes separated; clock probe correct; phases
  identifiability-flagged; no in-window snapshots).
- CI green on both matrix legs on every merged PR head.
- Post-merge integration review: no cross-stream defects; 2-model matrix
  gen + sentinel validate-config + mock campaign subset verified.

## Known Workspace State

- `main` is pushed and current (through this session's bookkeeping).
- No worktrees remain (both removed after their PRs merged).
- `/tmp/jw-lead-verify/` holds disposable lead-verification artifacts.

## What Is Next

Follow `TASK_QUEUE.md` (lane-annotated). In order:

1. **Suite implementation** [AGENT] — P2-010a/b, P2-012 phase 1, P2-020
   generators, per D-042 + the research handoff (rank 3 row P2-010; the
   queue's quiet-lane rows 1-2 stay top for the next quiet window).
2. **P2-015 then P2-006 in quiet Window A** [QUIET-MAC].
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
