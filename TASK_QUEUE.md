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
6. Decide whether the task is:
   - urgent workspace hygiene,
   - Phase 1 evidence work,
   - Phase 2 implementation prep,
   - later-phase research work,
   - documentation/reporting,
   - or unrelated/new scope.
7. Place or update the task in the queue with priority, rationale, evidence,
   and blockers.
8. If executing it now, say why it outranks the current top task.

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

## Current Queue

| Rank | ID | Priority | Status | Task | Evidence / Acceptance |
|---:|---|---|---|---|---|
| 1 | P1-001 | P1 Phase Gate | open | Capture supervisor approval and scope notes | Dated notes in `docs/phase_1/phase_1_exit_checklist.md`; `RUN_STATE.md` updated if scope changes |
| 2 | P1-002 | P1 Phase Gate | waiting-user | Complete Mac-local Phase 1 telemetry/runtime evidence | User handles local auth 2026-06-10; then capture one privileged `powermetrics` sample, record fields, and install the D-004 sudoers rule (exit-checklist instrumentation section); MLX install path still pending |
| 3 | P1-008 | P1 Phase Gate | waiting-user | Map phases to academic calendar | Colloquium/report dates + borrow window entered in `docs/milestones.md`; phase target dates derived |
| 4 | P1-003 | P1 Phase Gate | open | Record wall-meter decision | Meter make/model or "unavailable" verdict plus measurement/export method (exit-checklist wall-meter section; informs D-018 boundary calibration) |
| 5 | P1-004 | P1 Phase Gate | partial | Fill network/interconnect topology plan | Physical topology, link-speed paths, and throughput method recorded in the exit-checklist network section |
| 6 | P1-005 | P1 Phase Gate | open | Complete Hailo feasibility verdict | Verdict code and evidence in the exit-checklist Hailo section |
| 7 | P1-006 | P1 Phase Gate | open | Confirm NVIDIA/Orin telemetry access paths | SSH/runtime/telemetry command evidence in the exit-checklist instrumentation section, or marked pending with blocker (gates slices 2K/2L) |
| 8 | P1-007 | P1 Phase Gate | open | Perform Phase 2 readiness review | `docs/phase_1/phase_1_exit_checklist.md` states mock-first Phase 2 can begin |
| 9 | P2-001 | P2 Next Slice | queued | Mock vertical slice: slices 2A-2E per `docs/phase_2/phase_2_plan.md` | One command creates a complete mock run bundle; `validate-bundle` green; CI runs the mock end-to-end |
| 10 | P2-002 | P2 Next Slice | queued | Repetitions + experiment manifests (slice 2F) | 3-rep mock experiment test; manifest contract per D-005 |
| 11 | P2-004 | P2 Next Slice | queued | Close model selection (D-016) | Decision-log entry: models, revisions, artifact paths, local mirror, fallback candidate |
| 12 | P2-003 | P2 Next Slice | queued | Mac MLX + powermetrics vertical slice (slices 2G-2I) | Gated on P1-002 evidence + D-016; real bundle + 3-rep variance in a run report |
| 13 | P3-000 | P3 Research Expansion | queued | KV persistence feasibility spikes (Phase 3 Stage 3.0) | Verdicts in `docs/phase_3/kv_feasibility.md`; gated on Mac slice; must complete before any borrow-window scheduling |

## Completed Queue Items

| ID | Priority | Completed | Task | Evidence |
|---|---|---|---|---|
| Q-000 | P0 Safety | 2026-06-09 | Resolve the local `Energy_Benchmark_Architecture.docx` deletion decision | User confirmed the Word doc was unrelated; deletion committed in `a5d7404` |
| PLAN-001 | P1 Phase Gate | 2026-06-09 | Build evidence-shaped plans for Phases 2-5 (user-directed) | Per-phase plan + exit-checklist docs; `docs/decision_log.md` (D-001..D-019); `docs/risk_register.md`; `docs/milestones.md`; methodology/bundle-layout amendments; `AGENT_PLAN.md` restructured as index; run report `docs/run_reports/2026-06-09-phase-2-5-planning-buildout.md` |
| CI-001 | P2 Next Slice | 2026-06-09 | Add core-tests CI workflow (D-017) | `.github/workflows/ci.yml`; green check on push pending first remote run |
| DOC-001 | P4 Polish | 2026-06-09 | Unify Phase 1 doc scheme with Phases 2-5 (user-directed) | `docs/phase_1/` reduced to `phase_1_plan.md` + `phase_1_exit_checklist.md` (evidence dossier, all recorded evidence preserved); contracts moved to `docs/contracts/`; all live cross-references updated; run report `docs/run_reports/2026-06-09-phase-1-doc-unification.md` |
| DOC-002 | P4 Polish | 2026-06-09 | Add advisor-facing status/plan/architecture doc + audit original sketch (user-directed) | Root `PROJECT_STATUS.md` (standalone, mirrors the original architecture sketch's shape, includes sketch-evolution audit table); maintenance rule in `AGENT_PLAN.md`/`RUN_STATE.md`; run report `docs/run_reports/2026-06-09-advisor-status-doc.md` |

## Current Do-Not-Do-Yet List

- Do not start dashboard/report polish before the mock bundle/reducer path
  exists (slices 2A-2E).
- Do not start live MLX/powermetrics implementation before the mock lifecycle
  is runnable.
- Do not spend time on Hailo implementation until feasibility has a verdict.
- Do not implement schema v0.2 before Phase 3 Stage 3.1 (design is fixed in
  D-008; implementation waits).
- Do not schedule the 3080 Ti borrow window before Stage 3.0 verdicts and the
  rehearsed runbook exist (R-006).
- Do not start Phase 3 live-split work (3.3) before offline replay (3.2) has
  produced data.

## Queue Maintenance

At the end of substantial work:

- Update statuses in this file.
- Add new tasks discovered during the run.
- Move completed tasks below or mark them `done`.
- Update `RUN_STATE.md` with the next highest-ranked task.
