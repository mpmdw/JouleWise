# JouleWise Run State

Last updated: 2026-07-05

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

At the end of substantial work:

1. Update this file with what changed.
2. Update `TASK_QUEUE.md` with completed, added, or re-ranked tasks.
3. Add or update a detailed report in `docs/run_reports/`.
4. Record tests, commands, blockers, and the next best task.
5. Record new decision-log entries and any risk-register status changes.
6. Refresh `PROJECT_STATUS.md` if advisor-visible state changed.
7. Call out any dirty working-tree state that should not be accidentally
   committed.

## Current Project Status

Phase 1 is in its final stretch (remaining gates need external/hardware
input; per-item status in `docs/phase_1/phase_1_exit_checklist.md`).
Phase 2's hardware-independent core (2A-2F, 2J) is complete and runnable;
the new Slice 2N (pre-hardware hardening, ungated) is the top
implementable work; the hardware slices stay gated. Work paused
2026-06-13 through 2026-07-04 (planned break, recorded in
`docs/milestones.md`).

## What The Latest Run Did (2026-07-06, architecture review intake)

Full detail: `docs/run_reports/2026-07-06-architecture-review-intake.md`.
An external architecture review (Codex) was triaged; agreed items landed
as design decisions and plan updates: **D-024** (adapters receive an
immutable `RunContext` — settles 2N.1's open seam question), **D-025**
(shared `BundleReader` for reducer/report/validate/aggregate — new item
2N.8; 2N.7 must build on it), a new cross-cutting contract
`docs/contracts/node_worker_protocol.md` (remote execution shape, pinned
during 2K, reused by 2L + Phase 3), item 2N.9 (design-only v0.2
compatibility check), and a sqlite-before-DuckDB clause in Stage 4.1.
Operational note: agent sessions should be launched from
`~/code/CapstoneRivoire/Capstone`; the old Desktop path holds only a
harness-recreated `.claude/settings.local.json` and can be deleted after
relaunch. A same-day second review pass confirmed the intake and drove
three housekeeping fixes (D-024/D-025 "pending" wording, R-017 marked
mitigated, 2N three-commit grouping in playbook M1).

## Previous Run (2026-07-05, docs/meta-layer cleanup + repo move)

Full detail: `docs/run_reports/2026-07-05-docs-meta-cleanup.md`. Summary:

- External audit (code review + planning review) on return from the
  break; suite verified green (169) before any changes.
- D-023: per-item status consolidated into the exit checklists; plan
  headers now point there; `phase_2_plan.md` vs hardware-guide
  duplication cut to a what/how split.
- Drift fixed: phase 1 plan step statuses, stale 2026-06-10 auth-session
  references everywhere, D-019→D-022 range, 2M gate wording (Mac-only
  floor allowed), `PROJECT_STATUS.md` stale test count.
- New: Slice 2N (pre-hardware hardening, from the code review's seam
  findings); Phase 4 Stage 4.6 (background/related-work draft —
  previously unowned); R-016 (corpus backup); R-017 (iCloud lock);
  milestones heartbeat rule; queue tasks P0-002, P2-007, P3-001.
- The iCloud EPERM lock recurred mid-run (R-017); the user moved the
  repo off iCloud in response (P0-001, done — see below).
- Advisor doc (`PROJECT_STATUS.md`) refreshed for 2026-07-05.

## Current Verification

```bash
python3 -m unittest discover -s tests
```

Result (2026-07-05, at the new repo location, after all changes):
`Ran 169 tests, OK (skipped=8)` — the 8 skips are the
`[analysis]`-extra chart tests.

## Known Workspace State

- **Repo moved 2026-07-05:** the canonical path is now
  `~/code/CapstoneRivoire/Capstone` (off the iCloud-synced Desktop, per
  R-017, after the EPERM lock recurred mid-run). Git and the suite were
  verified green at the new path. Any stale `~/Desktop/CapstoneRivoire`
  references in shells/editors should be repointed.
- Remote: `git@github.com:mpmdw/JouleWise.git`; branch `main`.
- The 2026-07-05 cleanup changes are uncommitted at handoff (the lock
  blocked `.git` during the run; commit them as one docs/meta-cleanup
  commit). Insurance copies live in `~/jw_pending_edits/`; delete that
  directory once the commit lands and pushes.

## What Is Next

Follow `TASK_QUEUE.md`; execute via the mission guides in
`docs/agent_playbook.md` (start every session with its Mission M0). In
order:

1. P2-007: Slice 2N pre-hardware hardening — top ungated implementation
   work (playbook Mission M1; spec in `phase_2_plan.md` Slice 2N — now
   nine items; D-024/D-025 are pre-decided, implement them).
2. P0-002: corpus backup protocol (R-016) — must close before 2I data
   (playbook M2; needs the user to name a destination).
3. P3-001: related-work draft (Stage 4.6) — ungated desk filler
   (playbook M3).
4. The external gates when the user can: P1-001 (scope), P1-002 (auth
   session, rescheduled), P1-008 (calendar), P1-003/P1-004/P1-006 —
   these open playbook missions M4-M8.

Done 2026-07-05 (second commit of the day): cleanup commit `ae48abe`
pushed, CI run #7 green on main (mock e2e included) — Phase 2 CI row
closed; agent playbook added; Stage 4.6 seeded with the named 2025-26
competitor set from a landscape search.

## Open Decisions And Blockers

- Supervisor approval and scope pending (P1-001, R-001 — trigger fired
  2026-06-12, mitigation holding); also gates D-016.
- Calendar dates pending (P1-008, R-012).
- Wall-meter decision pending (P1-003, R-007).
- Physical network topology pending (P1-004, R-011).
- NVIDIA/Orin access evidence pending (P1-006; gates 2K/2L).
- Mac privileged powermetrics sample pending (P1-002, R-002; gates 2H;
  auth session to be rescheduled).
- D-016 model selection open (criteria fixed; needs P1-001 + install
  evidence).
- Git author identity was auto-selected as
  `Edr <edr@Edrs-MacBook-Air.local>` for the first commit. Amend future
  commits if a different identity is needed.
