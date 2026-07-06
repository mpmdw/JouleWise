# 2026-07-05: Docs/Meta-Layer Cleanup After Planned Break

## Context

Work paused 2026-06-13 through 2026-07-04 (planned vacation; recorded in
`docs/milestones.md` so the run-report gap reads as intentional). This run
resumed with a full external review of the repository state and planning
corpus (code review + planning audit via subagents), then executed the
docs/meta-layer cleanup the user approved. No production code changed in
this run; code findings were converted into a planned, ungated slice (2N)
and queued.

## Planning Reflection

Performed per `docs/planning_reflection_protocol.md` at run start:

- The audit found the corpus internally strong but with same-day status
  drift across its six status surfaces, two dangling references to the
  passed 2026-06-10 auth-session date, one gate-wording conflict (2M), a
  stale test count in `PROJECT_STATUS.md`, near-verbatim duplication
  between `phase_2_plan.md` and the hardware slice guide, and two
  planning gaps (related-work chapter unowned; no backup plan for the
  measurement corpus).
- The code review confirmed the mock core delivers what is claimed and
  identified pre-hardware seam work that should land before 2G/2H
  (captured as Slice 2N below), none of it architectural.

## What Changed

Status-authority consolidation (new decision D-023):

- Per-item phase status now lives solely in each phase's exit checklist.
- All five `phase_N_plan.md` headers now point at their checklist instead
  of carrying their own status line; per-step "Status:" lines were removed
  from `phase_1_plan.md`.
- `AGENT_PLAN.md`'s source-of-truth map updated: exit checklists own
  per-item status; `AGENT_PLAN.md` keeps a coarse mirror.

Drift fixes:

- `phase_1_plan.md`: Hailo verdict and Phase 2 readiness review moved from
  "Remaining" to complete (both closed 2026-06-12); stale per-step status
  lines removed; 2026-06-10 auth-session references replaced with
  "to be rescheduled".
- `phase_1_exit_checklist.md`: decision-log range D-001..D-019 corrected
  to D-001..D-022; Mac instrumentation rows updated for the passed
  auth-session date.
- `phase_2_exit_checklist.md`: 2M gate wording aligned with the plan
  (Mac-only is the documented floor, not forbidden).
- `PROJECT_STATUS.md`: repository-map test count 14 -> 169; CI claim
  restated as locally-verified + CI-enforced (remote run not re-verified
  this session; `gh` unauthenticated); dated update section rewritten for
  2026-07-05.
- `docs/milestones.md`: 2026-06-10 auth session marked passed-unused /
  reschedule; vacation window recorded; heartbeat rule added (a >14-day
  run-report gap outside a recorded break triggers a milestones/risk
  review at the next session start).
- `docs/risk_register.md`: R-001 trigger firing recorded (2A-2F complete
  2026-06-12 with P1-001 open; mitigation holding); R-002 stale date
  rationale fixed; new R-016 (measurement-corpus loss; backup protocol
  required before first real data) and R-017 (repo on iCloud-synced
  Desktop; EPERM lock recurrence — observed live during this very run).

Deduplication:

- `phase_2_plan.md` gated slices (2G/2H/2K/2L) now own the what/when/done
  (objective, gates, evidence, acceptance, fallback) and point to
  `hardware_slice_implementation_guide.md` for the how; the guide's
  duplicated gate/acceptance/fallback blocks were cut to pointers, and its
  2I/2M/D-016 restatements reduced to stubs. One fact, one home.

New planning content:

- `phase_2_plan.md` Slice 2N (pre-hardware hardening; ungated): raw
  telemetry seam (`write_raw`), measured-window/sampler-startup ordering,
  reducer token-count fallback, rail-timestamp contract hardening,
  config-schema null-acceptance fix, `reduce` CLI verb + structured
  reducer failures, report/reducer rail-fallback alignment. Added to the
  Phase 2 exit checklist and `AGENT_PLAN.md`.
- `phase_4_plan.md` Stage 4.6 (background and related-work draft;
  ungated desk work, may start any time) + exit-checklist row; feeds
  Stage 5.5 report assembly.
- `TASK_QUEUE.md`: new tasks for 2N, the backup protocol (R-016), the
  iCloud repo move (R-017), and the related-work draft; statuses updated.
- `README.md`: rerun-collision note (bundles are immutable; second
  identical run into the same runs dir errors by design).

## Environment Incident (recurrence)

The 2026-06-12 iCloud EPERM lock recurred during this run: `docs/`,
`joulewise/`, `tests/`, `.git`, and the repo root all returned
`Operation not permitted` on readdir/open for a period mid-run, with the
iCloud file provider mid-sync (`brctl status` showed an active full-sync).
Work continued from already-read content and /tmp drafts until the lock
cleared, then edits were applied and the suite re-run. This is now risk
R-017 — and the durable fix landed the same day: the user moved the repo
to `~/code/CapstoneRivoire/Capstone` (P0-001 complete; git + suite
verified green at the new path).

## Commands Run

```bash
python3 -m unittest discover -s tests   # 169 tests, OK (8 skips), before and after
git ls-files                            # confirmed venv/caches untracked
gh run list --repo mpmdw/JouleWise      # unauthenticated; CI not re-verified remotely
```

## What Passed / Failed

- Test suite green before and after (docs-only changes; run as a guard).
- Remote CI verification not possible this session (`gh` not logged in);
  the Phase 2 exit-checklist CI row stays "pending push verification".

## Next Agent Should

1. Commit this run's changes as one docs/meta-cleanup commit, push, and
   confirm CI green (closes the Phase 2 checklist's "pending push
   verification" row).
2. Slice 2N (pre-hardware hardening) — the top ungated implementation
   work; see `phase_2_plan.md` and queue task P2-007.
3. User-owned: schedule the local auth session (P1-002) and define the
   backup protocol (P0-002) before any real measurement data lands.
   (P0-001, the iCloud repo move, completed 2026-07-05:
   `~/code/CapstoneRivoire/Capstone`.)

## Decision Log / Risk Register Deltas

- New: D-023 (status authority consolidation).
- Risk updates: R-001 trigger-fired note; R-002 rationale; new R-016,
  R-017.
